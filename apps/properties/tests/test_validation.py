import pytest
from decimal import Decimal

from apps.accounts.tests.factories import LandlordUserFactory, TenantUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory

pytestmark = pytest.mark.django_db


class TestPropertyValidation:
    def test_duplicate_property_code_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        PropertyFactory(landlord=landlord, code="DUP001")

        client = authenticated_client(landlord)
        response = client.post(
            "/api/properties/",
            {
                "name": "Another Property",
                "code": "DUP001",
                "location": "Nairobi",
            },
        )

        assert response.status_code == 400

    def test_admin_assigning_non_landlord_role_rejected(self, authenticated_client):
        from apps.accounts.tests.factories import AdminUserFactory

        admin = AdminUserFactory()
        tenant = TenantUserFactory()

        client = authenticated_client(admin)
        response = client.post(
            "/api/properties/",
            {
                "landlord": str(tenant.id),
                "name": "Bad Assignment",
                "code": "BAD001",
                "location": "Nairobi",
            },
        )

        assert response.status_code == 400
        assert "landlord" in response.data

    def test_landlord_auto_assigned_on_create(self, authenticated_client):
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)

        response = client.post(
            "/api/properties/",
            {"name": "Auto Assigned", "code": "AUTO001", "location": "Nairobi"},
        )

        assert response.status_code == 201
        assert str(response.data["landlord"] == str(landlord.id))

    def test_property_update_cannot_change_landlord(self, authenticated_client):
        landlord = LandlordUserFactory()
        other_landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)

        client = authenticated_client(landlord)
        response = client.patch(
            f"/api/properties/{property_obj.id}/",
            {"landlord": str(other_landlord.id), "location": "Changed"},
        )

        assert response.status_code == 200
        property_obj.refresh_from_db()
        assert property_obj.landlord == landlord  # unchanged, field is not writable here
        assert property_obj.location == "Changed"  # this field did update


class TestUnitValidation:
    def test_duplicate_unit_number_in_same_property_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        UnitFactory(property=property_obj, unit_number="A1")

        client = authenticated_client(landlord)
        response = client.post(
            "/api/properties/units/",
            {
                "property": str(property_obj.id),
                "unit_number": "A1",
                "rent_amount": 10000,
            },
        )

        assert response.status_code == 400
        assert "unit_number" in response.data

    def test_same_unit_number_allowed_across_different_properties(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_1 = PropertyFactory(landlord=landlord)
        property_2 = PropertyFactory(landlord=landlord)
        UnitFactory(property=property_1, unit_number="A1")

        client = authenticated_client(landlord)
        response = client.post(
            "/api/properties/units/",
            {
                "property": str(property_2.id),
                "unit_number": "A1",  # same number, different property — should be fine
                "rent_amount": 10000,
            },
        )

        assert response.status_code == 201

    def test_negative_rent_amount_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)

        client = authenticated_client(landlord)
        response = client.post(
            "/api/properties/units/",
            {
                "property": str(property_obj.id),
                "unit_number": "NEG1",
                "rent_amount": -5000,
            },
        )

        assert response.status_code == 400
        assert "rent_amount" in response.data

    def test_unit_update_cannot_change_property(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_1 = PropertyFactory(landlord=landlord)
        property_2 = PropertyFactory(landlord=landlord)
        unit_obj = UnitFactory(property=property_1)

        client = authenticated_client(landlord)
        response = client.patch(
            f"/api/properties/units/{unit_obj.id}/",
            {"property": str(property_2.id), "floor_number": 5},
        )

        assert response.status_code == 200
        unit_obj.refresh_from_db()
        assert unit_obj.property == property_1  # unchanged
        assert unit_obj.floor_number == 5  # this field did update