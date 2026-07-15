import pytest
from decimal import Decimal

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.properties.models import Unit

pytestmark = pytest.mark.django_db


class TestPropertyDashboard:
    def test_portfolio_summary_math(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_1 = PropertyFactory(landlord=landlord)
        property_2 = PropertyFactory(landlord=landlord)

        UnitFactory(property=property_1, status=Unit.Status.OCCUPIED, rent_amount=Decimal("20000"))
        UnitFactory(property=property_1, status=Unit.Status.VACANT, rent_amount=Decimal("15000"))
        UnitFactory(property=property_2, status=Unit.Status.OCCUPIED, rent_amount=Decimal("30000"))
        UnitFactory(property=property_2, status=Unit.Status.MAINTENANCE, rent_amount=Decimal("25000"))

        client = authenticated_client(landlord)
        response = client.get("/api/properties/dashboard/")

        assert response.status_code == 200
        data = response.data["data"]

        assert data["total_properties"] == 2
        assert data["total_units"] == 4
        assert data["occupied_units"] == 2
        assert data["vacant_units"] == 1
        assert data["maintenance_units"] == 1
        assert data["occupancy_rate"] == 50.0  # 2 occupied / 4 total
        assert Decimal(str(data["potential_monthly_rent"])) == Decimal("90000")  # sum of all 4

    def test_portfolio_summary_zero_units_no_crash(self, authenticated_client):
        landlord = LandlordUserFactory()
        PropertyFactory(landlord=landlord)  # no units attached

        client = authenticated_client(landlord)
        response = client.get("/api/properties/dashboard/")

        assert response.status_code == 200
        data = response.data["data"]

        assert data["total_units"] == 0
        assert data["occupancy_rate"] == 0.0
        assert data["potential_monthly_rent"] == 0

    def test_portfolio_summary_scoped_by_landlord(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()

        UnitFactory(property=PropertyFactory(landlord=landlord_a), rent_amount=Decimal("10000"))
        UnitFactory(property=PropertyFactory(landlord=landlord_b), rent_amount=Decimal("50000"))

        client = authenticated_client(landlord_a)
        response = client.get("/api/properties/dashboard/")

        data = response.data["data"]
        assert data["total_units"] == 1
        assert Decimal(str(data["potential_monthly_rent"])) == Decimal("10000")

    def test_portfolio_summary_admin_sees_everything(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        admin = AdminUserFactory()

        UnitFactory(property=PropertyFactory(landlord=landlord_a))
        UnitFactory(property=PropertyFactory(landlord=landlord_b))

        client = authenticated_client(admin)
        response = client.get("/api/properties/dashboard/")

        assert response.data["data"]["total_units"] == 2

    def test_per_property_occupancy_rate_in_list(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        UnitFactory(property=property_obj, status=Unit.Status.OCCUPIED, rent_amount=Decimal("10000"))
        UnitFactory(property=property_obj, status=Unit.Status.OCCUPIED, rent_amount=Decimal("10000"))
        UnitFactory(property=property_obj, status=Unit.Status.VACANT, rent_amount=Decimal("10000"))

        client = authenticated_client(landlord)
        response = client.get("/api/properties/")

        result = response.data["results"][0]
        assert result["occupancy_rate"] == pytest.approx(66.67, abs=0.01)  # 2/3


class TestUnitDashboard:
    def test_unit_dashboard_math(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)

        UnitFactory(property=property_obj, status=Unit.Status.OCCUPIED, rent_amount=Decimal("20000"))
        UnitFactory(property=property_obj, status=Unit.Status.OCCUPIED, rent_amount=Decimal("30000"))
        UnitFactory(property=property_obj, status=Unit.Status.VACANT, rent_amount=Decimal("25000"))
        UnitFactory(property=property_obj, status=Unit.Status.INACTIVE, rent_amount=Decimal("15000"))

        client = authenticated_client(landlord)
        response = client.get("/api/properties/units/dashboard/")

        assert response.status_code == 200
        data = response.data["data"]

        assert data["total_units"] == 4
        assert data["occupied_units"] == 2
        assert data["vacant_units"] == 1
        assert data["inactive_units"] == 1
        assert data["occupancy_rate"] == 50.0
        assert Decimal(str(data["average_rent"])) == Decimal("22500.00")  # (20k+30k+25k+15k)/4
        assert Decimal(str(data["potential_monthly_rent"])) == Decimal("90000")

    def test_unit_dashboard_zero_units_no_crash(self, authenticated_client):
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)
        response = client.get("/api/properties/units/dashboard/")

        assert response.status_code == 200
        data = response.data["data"]
        assert data["total_units"] == 0
        assert data["occupancy_rate"] == 0.0
        assert data["average_rent"] == 0

    def test_unit_dashboard_excludes_archived_units(self, authenticated_client):
        landlord = LandlordUserFactory()
        property_obj = PropertyFactory(landlord=landlord)
        active_unit = UnitFactory(property=property_obj, rent_amount=Decimal("10000"))
        archived_unit = UnitFactory(property=property_obj, rent_amount=Decimal("99999"))
        archived_unit.archive()

        client = authenticated_client(landlord)
        response = client.get("/api/properties/units/dashboard/")

        data = response.data["data"]
        assert data["total_units"] == 1
        assert Decimal(str(data["potential_monthly_rent"])) == Decimal("10000")