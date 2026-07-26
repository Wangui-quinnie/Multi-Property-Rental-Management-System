import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.tenants.models import Tenant
from apps.tenants.tests.factories import TenantFactory

pytestmark = pytest.mark.django_db


class TestTenantAccessControl:
    def test_admin_can_list_tenants(self, authenticated_client):
        admin = AdminUserFactory()
        TenantFactory()
        TenantFactory()

        client = authenticated_client(admin)
        response = client.get("/api/tenants/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_landlord_can_list_all_tenants(self, authenticated_client):
        landlord = LandlordUserFactory()
        active = TenantFactory(status=Tenant.Status.ACTIVE)
        inactive = TenantFactory(status=Tenant.Status.INACTIVE)
        blacklisted = TenantFactory(status=Tenant.Status.BLACKLISTED)

        client = authenticated_client(landlord)
        response = client.get("/api/tenants/")

        assert response.status_code == 200
        returned_ids = {row["id"] for row in response.data["results"]}
        assert returned_ids == {str(active.id), str(inactive.id), str(blacklisted.id)}

    def test_landlord_cannot_write_tenants(self, authenticated_client):
        landlord = LandlordUserFactory()
        tenant = TenantFactory()
        client = authenticated_client(landlord)

        create_response = client.post(
            "/api/tenants/",
            {"email": "blocked@example.com", "national_id": "44444444", "password": "SecurePass123!"},
        )
        update_response = client.patch(f"/api/tenants/{tenant.id}/", {"status": "INACTIVE"})

        assert create_response.status_code == 403
        assert update_response.status_code == 403

    def test_tenant_cannot_access_tenant_list(self, authenticated_client):
        tenant = TenantUserFactory()
        client = authenticated_client(tenant)
        response = client.get("/api/tenants/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/tenants/")
        assert response.status_code == 401