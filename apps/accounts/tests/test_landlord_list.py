# Covers the Admin-only landlord reference list added to support the
# frontend's "create property for a landlord" picker (Phase 2 of the
# frontend rebuild). Admin/Landlord/Tenant scoping mirrors the pattern
# used across the rest of the API.
import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory

pytestmark = pytest.mark.django_db


class TestLandlordList:
    def test_admin_can_list_landlords(self, authenticated_client):
        admin = AdminUserFactory()
        landlord_a = LandlordUserFactory(first_name="Ada", last_name="Landlord")
        landlord_b = LandlordUserFactory(first_name="Bob", last_name="Landlord")
        TenantUserFactory()  # should never appear in the results

        client = authenticated_client(admin)
        response = client.get("/api/auth/landlords/")

        assert response.status_code == 200
        assert response.data["success"] is True

        returned_ids = [row["id"] for row in response.data["data"]]
        assert str(landlord_a.id) in returned_ids
        assert str(landlord_b.id) in returned_ids
        assert len(response.data["data"]) == 2

    def test_response_only_exposes_id_full_name_email(self, authenticated_client):
        admin = AdminUserFactory()
        LandlordUserFactory()

        client = authenticated_client(admin)
        response = client.get("/api/auth/landlords/")

        row = response.data["data"][0]
        assert set(row.keys()) == {"id", "full_name", "email"}

    def test_landlord_cannot_access(self, authenticated_client):
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)
        response = client.get("/api/auth/landlords/")
        assert response.status_code == 403

    def test_tenant_cannot_access(self, authenticated_client):
        tenant = TenantUserFactory()
        client = authenticated_client(tenant)
        response = client.get("/api/auth/landlords/")
        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/auth/landlords/")
        assert response.status_code == 401
