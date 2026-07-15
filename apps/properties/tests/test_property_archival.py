import pytest

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.models import Property, Unit
from apps.properties.tests.factories import PropertyFactory, UnitFactory

pytestmark = pytest.mark.django_db


class TestPropertyArchival:
    def test_delete_archives_instead_of_hard_deleting(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)

        client = authenticated_client(landlord)
        response = client.delete(f"/api/properties/{property_obj.id}/")

        assert response.status_code == 204
        # Still exists in the DB, just excluded from the default manager
        assert Property.all_objects.filter(id=property_obj.id).exists()
        assert not Property.objects.filter(id=property_obj.id).exists()

    def test_archiving_property_cascades_to_units(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        unit_1 = UnitFactory(property=property_obj)
        unit_2 = UnitFactory(property=property_obj)

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/{property_obj.id}/")

        unit_1.refresh_from_db()
        unit_2.refresh_from_db()

        assert unit_1.is_archived is True
        assert unit_2.is_archived is True

    def test_archived_property_excluded_from_default_list(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/{property_obj.id}/")

        response = client.get("/api/properties/")
        ids = [p["id"] for p in response.data["results"]]
        assert str(property_obj.id) not in ids

    def test_archived_true_param_reveals_archived_property(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/{property_obj.id}/")

        response = client.get("/api/properties/?archived=true")
        ids = [p["id"] for p in response.data["results"]]
        assert str(property_obj.id) in ids

    def test_restore_reactivates_property_and_units(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        unit_obj = UnitFactory(property=property_obj)

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/{property_obj.id}/")
        response = client.post(f"/api/properties/{property_obj.id}/restore/")

        assert response.status_code == 200

        property_obj.refresh_from_db()
        unit_obj.refresh_from_db()

        assert property_obj.is_archived is False
        assert unit_obj.is_archived is False

    def test_cannot_create_unit_on_archived_property(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        property_obj.archive()

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