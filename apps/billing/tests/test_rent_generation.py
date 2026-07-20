import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import BillingPeriod, Invoice
from apps.billing.tests.factories import BillingPeriodFactory

pytestmark = pytest.mark.django_db


class TestRentInvoiceGeneration:
    def test_landlord_generates_invoices_scoped_to_own_leases(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()

        lease_a = LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord_a)),
            status=Lease.Status.ACTIVE,
        )
        LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord_b)),
            status=Lease.Status.ACTIVE,
        )

        billing_period = BillingPeriodFactory()

        client = authenticated_client(landlord_a)
        response = client.post(
            "/api/billing/invoices/generate-rent/",
            {"billing_period": str(billing_period.id)},
        )

        assert response.status_code == 201
        invoices = response.data["data"]
        assert len(invoices) == 1
        assert str(invoices[0]["lease"]) == str(lease_a.id)

    def test_admin_generates_invoices_for_all_landlords(self, authenticated_client):
        admin = AdminUserFactory()

        LeaseFactory(status=Lease.Status.ACTIVE)
        LeaseFactory(status=Lease.Status.ACTIVE)

        billing_period = BillingPeriodFactory()

        client = authenticated_client(admin)
        response = client.post(
            "/api/billing/invoices/generate-rent/",
            {"billing_period": str(billing_period.id)},
        )

        assert response.status_code == 201
        assert len(response.data["data"]) == 2

    def test_generation_is_idempotent(self, authenticated_client):
        landlord = LandlordUserFactory()
        LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord)),
            status=Lease.Status.ACTIVE,
        )
        billing_period = BillingPeriodFactory()

        client = authenticated_client(landlord)
        client.post("/api/billing/invoices/generate-rent/", {"billing_period": str(billing_period.id)})
        client.post("/api/billing/invoices/generate-rent/", {"billing_period": str(billing_period.id)})

        assert Invoice.objects.filter(billing_period=billing_period).count() == 1

    def test_inactive_leases_excluded_from_generation(self, authenticated_client):
        landlord = LandlordUserFactory()
        LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord)),
            status=Lease.Status.ENDED,
        )
        billing_period = BillingPeriodFactory()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/billing/invoices/generate-rent/",
            {"billing_period": str(billing_period.id)},
        )

        assert response.status_code == 201
        assert len(response.data["data"]) == 0

    def test_tenant_cannot_generate_invoices(self, authenticated_client):
        tenant_profile = TenantFactory()
        billing_period = BillingPeriodFactory()

        client = authenticated_client(tenant_profile.user)
        response = client.post(
            "/api/billing/invoices/generate-rent/",
            {"billing_period": str(billing_period.id)},
        )

        assert response.status_code == 403

    def test_cannot_generate_for_closed_billing_period(self, authenticated_client):
        landlord = LandlordUserFactory()
        LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord)),
            status=Lease.Status.ACTIVE,
        )
        billing_period = BillingPeriodFactory(status=BillingPeriod.Status.CLOSED)

        client = authenticated_client(landlord)
        response = client.post(
            "/api/billing/invoices/generate-rent/",
            {"billing_period": str(billing_period.id)},
        )

        assert response.status_code == 400

    def test_invoice_totals_match_lease_rent_amount(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease = LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord)),
            status=Lease.Status.ACTIVE,
            rent_amount=27500,
        )
        billing_period = BillingPeriodFactory()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/billing/invoices/generate-rent/",
            {"billing_period": str(billing_period.id)},
        )

        invoice_data = response.data["data"][0]
        assert float(invoice_data["subtotal"]) == 27500.0
        assert float(invoice_data["total_amount"]) == 27500.0
        assert float(invoice_data["balance"]) == 27500.0
        assert invoice_data["status"] == "UNPAID"
        assert len(invoice_data["items"]) == 1
        assert invoice_data["items"][0]["item_type"] == "RENT"