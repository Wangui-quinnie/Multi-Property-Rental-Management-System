import pytest
from decimal import Decimal

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import Invoice
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease
from apps.payments.models import Payment, PaymentAllocation
from apps.payments.tests.factories import PaymentFactory
from datetime import date, timedelta

pytestmark = pytest.mark.django_db


def _make_lease_with_invoice(landlord=None, rent_amount=20000):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=rent_amount)
    billing_period = BillingPeriodFactory(due_date=date.today() + timedelta(days=10))
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return lease, invoice, landlord

class TestManualAllocation:
    def test_allocate_updates_invoice_balance(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=20000)
        payment = PaymentFactory(tenant=lease.tenant, amount=20000)

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "20000.00"},
        )

        assert response.status_code == 201

        invoice.refresh_from_db()
        assert invoice.amount_paid == Decimal("20000.00")
        assert invoice.balance == Decimal("0.00")
        assert invoice.status == Invoice.Status.PAID

    def test_partial_allocation_sets_partially_paid(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=20000)
        payment = PaymentFactory(tenant=lease.tenant, amount=8000)

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "8000.00"},
        )

        assert response.status_code == 201
        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PARTIALLY_PAID
        assert invoice.balance == Decimal("12000.00")

    def test_overdue_invoice_partially_paid_stays_overdue(self, authenticated_client):
        """
        Regression guard for the refresh_totals() delegation fix:
        partially paying an OVERDUE invoice must not silently revert
        it to PARTIALLY_PAID if the due date has genuinely passed —
        refresh_totals() prioritizes OVERDUE over PARTIALLY_PAID.
        """
        from datetime import date, timedelta

        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=20000)

        past_start = date.today() - timedelta(days=400)
        billing_period = BillingPeriodFactory(
            start_date=past_start,
            end_date=past_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=10),  # already overdue
        )
        invoice = generate_rent_invoice_for_lease(lease, billing_period)
        assert invoice.status == Invoice.Status.OVERDUE

        payment = PaymentFactory(tenant=lease.tenant, amount=8000)

        client = authenticated_client(landlord)
        client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "8000.00"},
        )

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.OVERDUE  # not reverted to PARTIALLY_PAID
        assert invoice.balance == Decimal("12000.00")

    def test_overdue_invoice_fully_paid_becomes_paid(self, authenticated_client):
        from datetime import date, timedelta

        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=15000)

        past_start = date.today() - timedelta(days=400)
        billing_period = BillingPeriodFactory(
            start_date=past_start,
            end_date=past_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=10),
        )
        invoice = generate_rent_invoice_for_lease(lease, billing_period)
        assert invoice.status == Invoice.Status.OVERDUE

        payment = PaymentFactory(tenant=lease.tenant, amount=15000)

        client = authenticated_client(landlord)
        client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "15000.00"},
        )

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PAID  # PAID still wins over OVERDUE

    def test_allocation_exceeding_invoice_balance_rejected(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=10000)
        payment = PaymentFactory(tenant=lease.tenant, amount=50000)

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "50000.00"},  # invoice balance is only 10000
        )

        assert response.status_code == 400

    def test_allocation_exceeding_payment_amount_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease_1, invoice_1, _ = _make_lease_with_invoice(landlord=landlord, rent_amount=10000)
        lease_2, invoice_2, _ = _make_lease_with_invoice(landlord=landlord, rent_amount=10000)

        # Same tenant, two invoices, but payment only covers one
        invoice_2.lease.tenant = lease_1.tenant
        payment = PaymentFactory(tenant=lease_1.tenant, amount=5000)

        client = authenticated_client(landlord)
        first = client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice_1.id), "amount": "3000.00"},
        )
        assert first.status_code == 201

        second = client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice_1.id), "amount": "3000.00"},  # 3000 + 3000 > 5000 payment
        )

        assert second.status_code == 400

    def test_tenant_mismatch_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease, invoice, _ = _make_lease_with_invoice(landlord=landlord)

        other_tenant_lease, _, _ = _make_lease_with_invoice(landlord=landlord)
        payment = PaymentFactory(tenant=other_tenant_lease.tenant, amount=20000)

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "10000.00"},
        )

        assert response.status_code == 400  # payment's tenant != invoice's tenant

    def test_landlord_cannot_allocate_unowned_payment(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        lease, invoice, landlord_b = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, amount=20000)

        client = authenticated_client(landlord_a)
        response = client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "10000.00"},
        )

        assert response.status_code == 404  # blocked at queryset scoping


class TestAllocateOldest:
    def test_splits_across_multiple_overdue_invoices_oldest_first(self, authenticated_client):
        from datetime import date, timedelta

        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=10000)

        old_start = date.today() - timedelta(days=400)
        old_period = BillingPeriodFactory(
            start_date=old_start,
            end_date=old_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=40),
        )
        newer_start = date.today() - timedelta(days=300)
        newer_period = BillingPeriodFactory(
            start_date=newer_start,
            end_date=newer_start + timedelta(days=29),
            due_date=date.today() + timedelta(days=10),
        )

        old_invoice = generate_rent_invoice_for_lease(lease, old_period)
        newer_invoice = generate_rent_invoice_for_lease(lease, newer_period)

        payment = PaymentFactory(tenant=lease.tenant, amount=15000)

        client = authenticated_client(landlord)
        response = client.post(f"/api/payments/{payment.id}/allocate-oldest/")

        assert response.status_code == 201

        old_invoice.refresh_from_db()
        newer_invoice.refresh_from_db()

        assert old_invoice.status == Invoice.Status.PAID  # fully paid first (oldest)
        assert old_invoice.balance == 0

        assert newer_invoice.balance == Decimal("5000.00")  # remaining 15000 - 10000
        assert newer_invoice.status == Invoice.Status.PARTIALLY_PAID

    def test_allocate_oldest_stops_when_payment_exhausted(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease, invoice_1, _ = _make_lease_with_invoice(landlord=landlord, rent_amount=10000)

        payment = PaymentFactory(tenant=lease.tenant, amount=5000)

        client = authenticated_client(landlord)
        response = client.post(f"/api/payments/{payment.id}/allocate-oldest/")

        data = response.data["data"]
        assert float(data["total_allocated"]) == 5000.0
        assert float(data["unallocated_amount"]) == 0.0

    def test_landlord_cannot_trigger_allocate_oldest_for_unowned_payment(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        lease, invoice, landlord_b = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, amount=20000)

        client = authenticated_client(landlord_a)
        response = client.post(f"/api/payments/{payment.id}/allocate-oldest/")

        assert response.status_code == 404


class TestRemoveAllocation:
    def test_removing_allocation_reverts_invoice_balance(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=20000)
        payment = PaymentFactory(tenant=lease.tenant, amount=20000)

        client = authenticated_client(landlord)
        allocate_response = client.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "20000.00"},
        )

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PAID

        allocation_id = allocate_response.data["data"]["allocations"][0]["id"]

        response = client.post(f"/api/payments/{payment.id}/allocations/{allocation_id}/remove/")

        assert response.status_code == 200

        invoice.refresh_from_db()
        assert invoice.amount_paid == Decimal("0.00")
        assert invoice.balance == Decimal("20000.00")
        assert invoice.status == Invoice.Status.UNPAID

        assert not PaymentAllocation.objects.filter(id=allocation_id).exists()

    def test_removing_allocation_from_unowned_payment_rejected(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        lease, invoice, landlord_b = _make_lease_with_invoice(rent_amount=10000)
        payment = PaymentFactory(tenant=lease.tenant, amount=10000)

        client_b = authenticated_client(landlord_b)
        allocate_response = client_b.post(
            f"/api/payments/{payment.id}/allocate/",
            {"invoice": str(invoice.id), "amount": "10000.00"},
        )
        allocation_id = allocate_response.data["data"]["allocations"][0]["id"]

        client_a = authenticated_client(landlord_a)
        response = client_a.post(f"/api/payments/{payment.id}/allocations/{allocation_id}/remove/")

        assert response.status_code == 404