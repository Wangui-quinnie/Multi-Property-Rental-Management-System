import pytest

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.properties.models import Property, Unit

pytestmark = pytest.mark.django_db


class TestPropertyFiltering:
    def test_filter_by_status(self, authenticated_client):
        landlord = LandlordUserFactory()
        PropertyFactory(landlord=landlord, status=Property.Status.ACTIVE)
        PropertyFactory(landlord=landlord, status=Property.Status.INACTIVE)

        client = authenticated_client(landlord)
        response = client.get("/api/properties/?status=INACTIVE")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["status"] == "INACTIVE"

    def test_filter_by_location_icontains(self, authenticated_client):
        landlord = LandlordUserFactory()
        PropertyFactory(landlord=landlord, location="Nairobi West")
        PropertyFactory(landlord=landlord, location="Mombasa")

        client = authenticated_client(landlord)
        response = client.get("/api/properties/?location=nairobi")

        results = response.data["results"]
        assert len(results) == 1
        assert "Nairobi" in results[0]["location"]

    def test_search_by_name(self, authenticated_client):
        landlord = LandlordUserFactory()
        PropertyFactory(landlord=landlord, name="Sunrise Apartments")
        PropertyFactory(landlord=landlord, name="Green Villas")

        client = authenticated_client(landlord)
        response = client.get("/api/properties/?search=Sunrise")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Sunrise Apartments"

    def test_ordering_by_name_descending(self, authenticated_client):
        landlord = LandlordUserFactory()
        PropertyFactory(landlord=landlord, name="Alpha")
        PropertyFactory(landlord=landlord, name="Zulu")

        client = authenticated_client(landlord)
        response = client.get("/api/properties/?ordering=-name")

        names = [p["name"] for p in response.data["results"]]
        assert names == ["Zulu", "Alpha"]


class TestUnitFiltering:
    def test_filter_by_status(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        UnitFactory(property=property_obj, status=Unit.Status.VACANT)
        UnitFactory(property=property_obj, status=Unit.Status.OCCUPIED)

        client = authenticated_client(landlord)
        response = client.get("/api/properties/units/?status=VACANT")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["status"] == "VACANT"

    def test_filter_by_property(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_1 = PropertyFactory(landlord=landlord)
        property_2 = PropertyFactory(landlord=landlord)
        UnitFactory(property=property_1)
        UnitFactory(property=property_2)

        client = authenticated_client(landlord)
        response = client.get(f"/api/properties/units/?property={property_1.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert str(results[0]["property"]) == str(property_1.id)

    def test_filter_by_rent_range(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        UnitFactory(property=property_obj, rent_amount=5000)
        UnitFactory(property=property_obj, rent_amount=15000)
        UnitFactory(property=property_obj, rent_amount=30000)

        client = authenticated_client(landlord)
        response = client.get("/api/properties/units/?min_rent=10000&max_rent=20000")

        results = response.data["results"]
        assert len(results) == 1
        assert float(results[0]["rent_amount"]) == 15000

    def test_search_by_unit_number(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        UnitFactory(property=property_obj, unit_number="Penthouse-1")
        UnitFactory(property=property_obj, unit_number="A102")

        client = authenticated_client(landlord)
        response = client.get("/api/properties/units/?search=Penthouse")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["unit_number"] == "Penthouse-1"