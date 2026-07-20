import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease

pytestmark = pytest.mark.django_db


def _make_invoice_for_landlord(landlord=None, tenant_profile=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease_kwargs = {"unit": unit, "status": Lease.Status.ACTIVE}
    if tenant_profile:
        lease_kwargs["tenant"] = tenant_profile
    lease = LeaseFactory(**lease_kwargs)
    billing_period = BillingPeriodFactory()
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return invoice, landlord, lease.tenant


class TestInvoiceScoping:
    def test_landlord_sees_only_own_invoices(self, authenticated_client):
        invoice_a, landlord_a, _ = _make_invoice_for_landlord()
        _make_invoice_for_landlord()  # unrelated landlord

        client = authenticated_client(landlord_a)
        response = client.get("/api/billing/invoices/")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(invoice_a.id)

    def test_admin_sees_all_invoices(self, authenticated_client):
        admin = AdminUserFactory()
        _make_invoice_for_landlord()
        _make_invoice_for_landlord()

        client = authenticated_client(admin)
        response = client.get("/api/billing/invoices/")

        assert len(response.data["results"]) == 2

    def test_tenant_sees_only_own_invoice(self, authenticated_client):
        from apps.tenants.tests.factories import TenantFactory

        tenant_profile = TenantFactory()
        invoice, _, _ = _make_invoice_for_landlord(tenant_profile=tenant_profile)
        _make_invoice_for_landlord()  # unrelated tenant

        client = authenticated_client(tenant_profile.user)
        response = client.get("/api/billing/invoices/")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(invoice.id)

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/billing/invoices/")
        assert response.status_code == 401

    def test_write_methods_not_exposed_on_invoices(self, authenticated_client):
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)

        response = client.post("/api/billing/invoices/", {})
        assert response.status_code == 405