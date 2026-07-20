import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.billing.models import BillingPeriod
from apps.billing.tests.factories import BillingPeriodFactory

pytestmark = pytest.mark.django_db


class TestBillingPeriodPermissions:
    def test_admin_can_create_billing_period(self, authenticated_client):
        admin = AdminUserFactory()
        client = authenticated_client(admin)

        response = client.post(
            "/api/billing/periods/",
            {
                "name": "January 2026",
                "start_date": "2026-01-01",
                "end_date": "2026-01-31",
                "due_date": "2026-01-05",
            },
        )

        assert response.status_code == 201
        assert BillingPeriod.objects.filter(name="January 2026").exists()

    def test_landlord_cannot_create_billing_period(self, authenticated_client):
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)

        response = client.post(
            "/api/billing/periods/",
            {
                "name": "February 2026",
                "start_date": "2026-02-01",
                "end_date": "2026-02-28",
                "due_date": "2026-02-05",
            },
        )

        assert response.status_code == 403

    def test_tenant_cannot_create_billing_period(self, authenticated_client):
        tenant = TenantUserFactory()
        client = authenticated_client(tenant)

        response = client.post(
            "/api/billing/periods/",
            {
                "name": "March 2026",
                "start_date": "2026-03-01",
                "end_date": "2026-03-31",
                "due_date": "2026-03-05",
            },
        )

        assert response.status_code == 403

    def test_landlord_can_read_billing_periods(self, authenticated_client):
        landlord = LandlordUserFactory()
        BillingPeriodFactory()

        client = authenticated_client(landlord)
        response = client.get("/api/billing/periods/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_tenant_can_read_billing_periods(self, authenticated_client):
        tenant = TenantUserFactory()
        BillingPeriodFactory()

        client = authenticated_client(tenant)
        response = client.get("/api/billing/periods/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/billing/periods/")
        assert response.status_code == 401

    def test_end_date_before_start_date_rejected(self, authenticated_client):
        admin = AdminUserFactory()
        client = authenticated_client(admin)

        response = client.post(
            "/api/billing/periods/",
            {
                "name": "Bad Period",
                "start_date": "2026-05-01",
                "end_date": "2026-04-01",
                "due_date": "2026-05-05",
            },
        )

        assert response.status_code == 400

    def test_due_date_before_start_date_rejected(self, authenticated_client):
        admin = AdminUserFactory()
        client = authenticated_client(admin)

        response = client.post(
            "/api/billing/periods/",
            {
                "name": "Bad Period 2",
                "start_date": "2026-06-01",
                "end_date": "2026-06-30",
                "due_date": "2026-05-01",
            },
        )

        assert response.status_code == 400

    def test_admin_can_update_billing_period_status(self, authenticated_client):
        admin = AdminUserFactory()
        period = BillingPeriodFactory(status=BillingPeriod.Status.OPEN)

        client = authenticated_client(admin)
        response = client.patch(f"/api/billing/periods/{period.id}/", {"status": "CLOSED"})

        assert response.status_code == 200
        period.refresh_from_db()
        assert period.status == BillingPeriod.Status.CLOSED