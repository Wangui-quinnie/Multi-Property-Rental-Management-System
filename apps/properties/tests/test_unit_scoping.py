import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory

pytestmark = pytest.mark.django_db


class TestUnitOwnershipScoping:
    def test_landlord_sees_only_own_units(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()

        property_a = PropertyFactory(landlord=landlord_a)
        property_b = PropertyFactory(landlord=landlord_b)

        unit_a = UnitFactory(property=property_a, unit_number="A1")
        UnitFactory(property=property_b, unit_number="B1")

        client = authenticated_client(landlord_a)
        response = client.get("/api/properties/units/")

        assert response.status_code == 200
        results = response.data["results"]
        returned_ids = [u["id"] for u in results]

        assert str(unit_a.id) in returned_ids
        assert len(results) == 1

    def test_admin_sees_all_units(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        admin = AdminUserFactory()

        UnitFactory(property=PropertyFactory(landlord=landlord_a))
        UnitFactory(property=PropertyFactory(landlord=landlord_b))

        client = authenticated_client(admin)
        response = client.get("/api/properties/units/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_tenant_cannot_access_units(self, authenticated_client):
        tenant = TenantUserFactory()
        client = authenticated_client(tenant)
        response = client.get("/api/properties/units/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/properties/units/")
        assert response.status_code == 401

    def test_landlord_cannot_retrieve_other_landlords_unit(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        other_unit = UnitFactory(property=PropertyFactory(landlord=landlord_b))

        client = authenticated_client(landlord_a)
        response = client.get(f"/api/properties/units/{other_unit.id}/")

        assert response.status_code == 404

    def test_landlord_cannot_create_unit_on_another_landlords_property(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        other_property = PropertyFactory(landlord=landlord_b)

        client = authenticated_client(landlord_a)
        response = client.post(
            "/api/properties/units/",
            {
                "property": str(other_property.id),
                "unit_number": "X1",
                "rent_amount": 10000,
            },
        )

        assert response.status_code == 403