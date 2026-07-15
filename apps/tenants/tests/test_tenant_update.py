import pytest

from apps.accounts.tests.factories import AdminUserFactory
from apps.tenants.models import Tenant
from apps.tenants.tests.factories import TenantFactory

pytestmark = pytest.mark.django_db


class TestTenantUpdate:
    def test_admin_updates_tenant_status(self, authenticated_client):
        admin = AdminUserFactory()
        tenant = TenantFactory(status=Tenant.Status.ACTIVE)

        client = authenticated_client(admin)
        response = client.patch(
            f"/api/tenants/{tenant.id}/",
            {"status": "BLACKLISTED"},
        )

        assert response.status_code == 200
        tenant.refresh_from_db()
        assert tenant.status == Tenant.Status.BLACKLISTED

    def test_update_does_not_expose_user_fields(self, authenticated_client):
        """
        TenantUpdateSerializer intentionally excludes User fields
        (name, phone, email) — those belong to the tenant's own
        profile endpoint, not admin-driven Tenant management.
        """
        admin = AdminUserFactory()
        tenant = TenantFactory()
        original_first_name = tenant.user.first_name

        client = authenticated_client(admin)
        client.patch(
            f"/api/tenants/{tenant.id}/",
            {"first_name": "ShouldNotChange", "emergency_contact_name": "New Contact"},
        )

        tenant.user.refresh_from_db()
        tenant.refresh_from_db()

        assert tenant.user.first_name == original_first_name
        assert tenant.emergency_contact_name == "New Contact"