import pytest

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.models import Unit
from apps.properties.tests.factories import PropertyFactory, UnitFactory

pytestmark = pytest.mark.django_db


class TestUnitArchival:
    def test_delete_archives_instead_of_hard_deleting(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit_obj = UnitFactory(property=PropertyFactory(landlord=landlord))

        client = authenticated_client(landlord)
        response = client.delete(f"/api/properties/units/{unit_obj.id}/")

        assert response.status_code == 204
        assert Unit.all_objects.filter(id=unit_obj.id).exists()
        assert not Unit.objects.filter(id=unit_obj.id).exists()

    def test_archived_unit_excluded_from_default_list(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit_obj = UnitFactory(property=PropertyFactory(landlord=landlord))

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/units/{unit_obj.id}/")

        response = client.get("/api/properties/units/")
        ids = [u["id"] for u in response.data["results"]]
        assert str(unit_obj.id) not in ids

    def test_archived_true_param_reveals_archived_unit(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit_obj = UnitFactory(property=PropertyFactory(landlord=landlord))

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/units/{unit_obj.id}/")

        response = client.get("/api/properties/units/?archived=true")
        ids = [u["id"] for u in response.data["results"]]
        assert str(unit_obj.id) in ids

    def test_restore_reactivates_unit(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit_obj = UnitFactory(property=PropertyFactory(landlord=landlord))

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/units/{unit_obj.id}/")
        response = client.post(f"/api/properties/units/{unit_obj.id}/restore/")

        assert response.status_code == 200

        unit_obj.refresh_from_db()
        assert unit_obj.is_archived is False

    def test_archiving_unit_does_not_affect_sibling_units(self, authenticated_client):
        """
        Unlike Property archival (which cascades to its Units), archiving
        a single Unit should have no effect on other units in the same
        property — there's nothing below Unit in the hierarchy to cascade to.
        """
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        unit_1 = UnitFactory(property=property_obj)
        unit_2 = UnitFactory(property=property_obj)

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/units/{unit_1.id}/")

        unit_2.refresh_from_db()
        assert unit_2.is_archived is False

    def test_archiving_unit_does_not_affect_parent_property(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        unit_obj = UnitFactory(property=property_obj)

        client = authenticated_client(landlord)
        client.delete(f"/api/properties/units/{unit_obj.id}/")

        property_obj.refresh_from_db()
        assert property_obj.is_archived is False