import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
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

    def test_landlord_cannot_access_tenants(self, authenticated_client):
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)
        response = client.get("/api/tenants/")

        assert response.status_code == 403

    def test_tenant_cannot_access_tenant_list(self, authenticated_client):
        tenant = TenantUserFactory()
        client = authenticated_client(tenant)
        response = client.get("/api/tenants/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/tenants/")
        assert response.status_code == 401