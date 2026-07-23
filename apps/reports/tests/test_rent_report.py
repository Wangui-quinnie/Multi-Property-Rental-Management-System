import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import InvoiceItem
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease
from apps.payments.tests.factories import PaymentFactory
from apps.payments.services import allocate_payment_to_invoice

pytestmark = pytest.mark.django_db


def _make_lease_with_invoice(landlord=None, rent_amount=20000, invoice_date=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=rent_amount)
    billing_period = BillingPeriodFactory(due_date=date.today() + timedelta(days=10))
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    if invoice_date:
        from apps.billing.models import Invoice
        Invoice.objects.filter(pk=invoice.pk).update(invoice_date=invoice_date)
        invoice.refresh_from_db()
    return lease, invoice, landlord


class TestRentReport:
    def test_rent_billed_matches_rent_line_items(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=25000)

        client = authenticated_client(landlord)
        response = client.get("/api/reports/rent/")

        assert response.status_code == 200
        data = response.data["data"]
        assert float(data["rent_billed"]) == 25000.0
        assert float(data["total_billed"]) == 25000.0

    def test_total_collected_reflects_amount_paid(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=20000)
        payment = PaymentFactory(tenant=lease.tenant, amount=20000)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=20000, user=landlord)

        client = authenticated_client(landlord)
        response = client.get("/api/reports/rent/")

        data = response.data["data"]
        assert float(data["total_collected"]) == 20000.0
        assert float(data["total_outstanding"]) == 0.0

    def test_outstanding_reflects_partial_payment(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=20000)
        payment = PaymentFactory(tenant=lease.tenant, amount=8000)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=8000, user=landlord)

        client = authenticated_client(landlord)
        response = client.get("/api/reports/rent/")

        data = response.data["data"]
        assert float(data["total_collected"]) == 8000.0
        assert float(data["total_outstanding"]) == 12000.0

    def test_rent_and_water_combined_in_total_but_rent_billed_stays_precise(self, authenticated_client):
        """
        Confirms the deliberate design: total_billed/total_collected
        can legitimately include water charges on the same invoice,
        but rent_billed stays exact since it's derived from
        InvoiceItem.item_type=RENT specifically.
        """
        from apps.billing.models import InvoiceItem

        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=20000)
        InvoiceItem.objects.create(
            invoice=invoice, item_type=InvoiceItem.ItemType.WATER,
            description="Water", quantity=1, unit_price=Decimal("3000.00"),
        )
        invoice.refresh_totals()

        client = authenticated_client(landlord)
        response = client.get("/api/reports/rent/")

        data = response.data["data"]
        assert float(data["rent_billed"]) == 20000.0  # unaffected by the water item
        assert float(data["total_billed"]) == 23000.0  # includes both

    def test_date_filtering_narrows_results(self, authenticated_client):
        landlord = LandlordUserFactory()
        old_lease, old_invoice, _ = _make_lease_with_invoice(
            landlord=landlord, rent_amount=10000, invoice_date=date(2025, 1, 15)
        )
        new_lease, new_invoice, _ = _make_lease_with_invoice(
            landlord=landlord, rent_amount=15000, invoice_date=date(2026, 6, 15)
        )

        client = authenticated_client(landlord)
        response = client.get("/api/reports/rent/?start_date=2026-01-01&end_date=2026-12-31")

        data = response.data["data"]
        assert float(data["rent_billed"]) == 15000.0  # only the 2026 invoice
        assert data["invoice_count"] == 1

    def test_landlord_sees_only_own_rent_data(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        _make_lease_with_invoice(landlord=landlord_a, rent_amount=10000)
        _make_lease_with_invoice(rent_amount=99999)  # unrelated landlord

        client = authenticated_client(landlord_a)
        response = client.get("/api/reports/rent/")

        assert float(response.data["data"]["rent_billed"]) == 10000.0

    def test_admin_sees_all_rent_data(self, authenticated_client):
        admin = AdminUserFactory()
        _make_lease_with_invoice(rent_amount=10000)
        _make_lease_with_invoice(rent_amount=15000)

        client = authenticated_client(admin)
        response = client.get("/api/reports/rent/")

        assert float(response.data["data"]["rent_billed"]) == 25000.0

    def test_tenant_cannot_access_rent_report(self, authenticated_client):
        tenant = TenantUserFactory()

        client = authenticated_client(tenant)
        response = client.get("/api/reports/rent/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/reports/rent/")
        assert response.status_code == 401