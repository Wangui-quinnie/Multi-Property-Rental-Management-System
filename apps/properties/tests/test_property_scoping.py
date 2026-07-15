# This test directly verifies role-based isolation of property data.
# It is a critical security test to ensure that landlords cannot access properties they do not own,
# and that tenants cannot access any property data. Admins should have full access.
import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.properties.tests.factories import PropertyFactory

pytestmark = pytest.mark.django_db


class TestPropertyOwnershipScoping:
    def test_landlord_sees_only_own_properties(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()

        prop_a = PropertyFactory(landlord=landlord_a, name="Landlord A's Property")
        PropertyFactory(landlord=landlord_b, name="Landlord B's Property")

        client = authenticated_client(landlord_a)
        response = client.get("/api/properties/")

        assert response.status_code == 200
        results = response.data["results"]
        returned_ids = [p["id"] for p in results]

        assert str(prop_a.id) in returned_ids
        assert len(results) == 1

    def test_admin_sees_all_properties(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        admin = AdminUserFactory()

        PropertyFactory(landlord=landlord_a)
        PropertyFactory(landlord=landlord_b)

        client = authenticated_client(admin)
        response = client.get("/api/properties/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_tenant_cannot_access_properties(self, authenticated_client):
        tenant = TenantUserFactory()
        client = authenticated_client(tenant)
        response = client.get("/api/properties/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/properties/")
        assert response.status_code == 401

    def test_landlord_cannot_retrieve_other_landlords_property(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        other_property = PropertyFactory(landlord=landlord_b)

        client = authenticated_client(landlord_a)
        response = client.get(f"/api/properties/{other_property.id}/")

        # Filtered out of the queryset entirely -> looks like it doesn't exist
        assert response.status_code == 404