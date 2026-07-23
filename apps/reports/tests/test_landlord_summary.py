import pytest
from datetime import date, timedelta

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease
from apps.occupancy.services import activate_occupancy

pytestmark = pytest.mark.django_db


class TestLandlordSummary:
    def test_summary_contains_all_sections(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord)
        response = client.get("/api/reports/landlord-summary/")

        assert response.status_code == 200
        data = response.data["data"]

        for key in ("occupancy", "vacancy", "arrears", "rent", "water", "cash_flow"):
            assert key in data

    def test_occupancy_section_matches_dedicated_dashboard(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
        activate_occupancy(lease=lease, user=landlord)

        client = authenticated_client(landlord)

        summary_response = client.get("/api/reports/landlord-summary/")
        dashboard_response = client.get("/api/properties/dashboard/")

        summary_occupancy = summary_response.data["data"]["occupancy"]
        dedicated_occupancy = dashboard_response.data["data"]

        assert summary_occupancy["total_units"] == dedicated_occupancy["total_units"]
        assert summary_occupancy["occupied_units"] == dedicated_occupancy["occupied_units"]
        assert float(summary_occupancy["occupancy_rate"]) == float(dedicated_occupancy["occupancy_rate"])

    def test_arrears_section_matches_dedicated_dashboard(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=10000)

        past_start = date.today() - timedelta(days=400)
        billing_period = BillingPeriodFactory(
            start_date=past_start,
            end_date=past_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=10),
        )
        generate_rent_invoice_for_lease(lease, billing_period)

        client = authenticated_client(landlord)

        summary_response = client.get("/api/reports/landlord-summary/")
        arrears_response = client.get("/api/billing/invoices/arrears/")

        assert (
            summary_response.data["data"]["arrears"]["portfolio_total_arrears"]
            == arrears_response.data["data"]["portfolio_total_arrears"]
        )

    def test_landlord_summary_scoped_to_own_data(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        unit_a = UnitFactory(property=PropertyFactory(landlord=landlord_a))
        LeaseFactory(unit=unit_a, status=Lease.Status.ACTIVE)

        landlord_b = LandlordUserFactory()
        unit_b = UnitFactory(property=PropertyFactory(landlord=landlord_b))
        LeaseFactory(unit=unit_b, status=Lease.Status.ACTIVE)
        LeaseFactory(unit=UnitFactory(property=PropertyFactory(landlord=landlord_b)), status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord_a)
        response = client.get("/api/reports/landlord-summary/")

        assert response.data["data"]["occupancy"]["total_units"] == 1

    def test_admin_summary_includes_all_landlords(self, authenticated_client):
        admin = AdminUserFactory()
        unit_a = UnitFactory(property=PropertyFactory(landlord=LandlordUserFactory()))
        LeaseFactory(unit=unit_a, status=Lease.Status.ACTIVE)
        unit_b = UnitFactory(property=PropertyFactory(landlord=LandlordUserFactory()))
        LeaseFactory(unit=unit_b, status=Lease.Status.ACTIVE)

        client = authenticated_client(admin)
        response = client.get("/api/reports/landlord-summary/")

        assert response.data["data"]["occupancy"]["total_units"] == 2

    def test_tenant_cannot_access_landlord_summary(self, authenticated_client):
        tenant = TenantUserFactory()

        client = authenticated_client(tenant)
        response = client.get("/api/reports/landlord-summary/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/reports/landlord-summary/")
        assert response.status_code == 401