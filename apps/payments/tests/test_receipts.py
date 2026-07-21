import pytest
from decimal import Decimal

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import Invoice
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease
from apps.payments.models import Payment
from apps.payments.tests.factories import PaymentFactory
from apps.payments.services import allocate_payment_to_invoice, allocate_payment_to_oldest_invoices

pytestmark = pytest.mark.django_db


def _make_lease_with_invoice(landlord=None, rent_amount=20000):
    from datetime import date, timedelta

    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=rent_amount)
    billing_period = BillingPeriodFactory(due_date=date.today() + timedelta(days=10))
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return lease, invoice, landlord


class TestReceiptRetrieval:
    def test_landlord_views_receipt_for_own_tenant_payment(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=15000)
        payment = PaymentFactory(tenant=lease.tenant, amount=15000)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=15000, user=landlord)

        client = authenticated_client(landlord)
        response = client.get(f"/api/payments/{payment.id}/receipt/")

        assert response.status_code == 200
        data = response.data["data"]

        assert data["receipt_number"].startswith("RCT-")
        assert data["payment_reference"] == payment.payment_reference
        assert float(data["amount_paid"]) == 15000.0
        assert len(data["allocations"]) == 1
        assert data["allocations"][0]["invoice_number"] == invoice.invoice_number
        assert float(data["allocations"][0]["amount_allocated"]) == 15000.0

    def test_tenant_views_receipt_for_own_payment(self, authenticated_client):
        """
        Confirms the permission swap: Tenant now has read access to
        their own payments (and receipts), where previously the
        viewset was Admin/Landlord only.
        """
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=10000)
        payment = PaymentFactory(tenant=lease.tenant, amount=10000)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=10000, user=landlord)

        client = authenticated_client(lease.tenant.user)
        response = client.get(f"/api/payments/{payment.id}/receipt/")

        assert response.status_code == 200
        assert response.data["data"]["payment_reference"] == payment.payment_reference

    def test_admin_views_any_receipt(self, authenticated_client):
        admin = AdminUserFactory()
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=12000)
        payment = PaymentFactory(tenant=lease.tenant, amount=12000)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=12000, user=landlord)

        client = authenticated_client(admin)
        response = client.get(f"/api/payments/{payment.id}/receipt/")

        assert response.status_code == 200

    def test_tenant_cannot_create_payment_after_permission_swap(self, authenticated_client):
        """
        Confirms Tenant's newly-granted read access did NOT accidentally
        loosen write permissions — creation must still be blocked.
        """
        lease, invoice, landlord = _make_lease_with_invoice()

        client = authenticated_client(lease.tenant.user)
        response = client.post(
            "/api/payments/",
            {
                "tenant": str(lease.tenant.id),
                "payment_reference": "PAY-SHOULD-FAIL",
                "payment_method": "CASH",
                "amount": "5000.00",
                "payment_date": "2026-01-15T10:00:00Z",
            },
        )

        assert response.status_code == 403

    def test_tenant_cannot_view_another_tenants_receipt(self, authenticated_client):
        lease_a, invoice_a, landlord = _make_lease_with_invoice(rent_amount=10000)
        payment_a = PaymentFactory(tenant=lease_a.tenant, amount=10000)
        allocate_payment_to_invoice(payment=payment_a, invoice=invoice_a, amount=10000, user=landlord)

        lease_b, _, _ = _make_lease_with_invoice()

        client = authenticated_client(lease_b.tenant.user)
        response = client.get(f"/api/payments/{payment_a.id}/receipt/")

        assert response.status_code == 404

    def test_landlord_cannot_view_unowned_tenants_receipt(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        lease, invoice, landlord_b = _make_lease_with_invoice(rent_amount=10000)
        payment = PaymentFactory(tenant=lease.tenant, amount=10000)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=10000, user=landlord_b)

        client = authenticated_client(landlord_a)
        response = client.get(f"/api/payments/{payment.id}/receipt/")

        assert response.status_code == 404

    def test_receipt_for_pending_payment_rejected(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, status=Payment.Status.PENDING)

        client = authenticated_client(landlord)
        response = client.get(f"/api/payments/{payment.id}/receipt/")

        assert response.status_code == 400

    def test_receipt_with_zero_allocations(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, amount=5000)

        client = authenticated_client(landlord)
        response = client.get(f"/api/payments/{payment.id}/receipt/")

        assert response.status_code == 200
        data = response.data["data"]
        assert data["allocations"] == []
        assert float(data["total_allocated"]) == 0.0
        assert float(data["unallocated_amount"]) == 5000.0

    def test_receipt_with_multiple_allocations_sums_correctly(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease, invoice_1, _ = _make_lease_with_invoice(landlord=landlord, rent_amount=8000)

        # second invoice, same lease/tenant
        from datetime import date, timedelta
        billing_period_2 = BillingPeriodFactory(due_date=date.today() + timedelta(days=40))
        invoice_2 = generate_rent_invoice_for_lease(lease, billing_period_2)

        payment = PaymentFactory(tenant=lease.tenant, amount=16000)
        allocate_payment_to_oldest_invoices(payment=payment, user=landlord)

        client = authenticated_client(landlord)
        response = client.get(f"/api/payments/{payment.id}/receipt/")

        data = response.data["data"]
        assert len(data["allocations"]) == 2
        assert float(data["total_allocated"]) == 16000.0
        assert float(data["unallocated_amount"]) == 0.0

    def test_unauthenticated_request_rejected(self, api_client):
        from apps.payments.tests.factories import PaymentFactory as PF
        payment = PF()
        response = api_client.get(f"/api/payments/{payment.id}/receipt/")
        assert response.status_code == 401