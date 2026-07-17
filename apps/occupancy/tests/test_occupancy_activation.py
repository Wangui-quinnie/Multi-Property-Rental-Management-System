import pytest
from datetime import date

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.properties.models import Unit
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.occupancy.models import Occupancy

pytestmark = pytest.mark.django_db


class TestOccupancyActivation:
    def test_landlord_activates_occupancy_on_own_unit(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord)
        response = client.post("/api/occupancy/activate/", {"lease": str(lease.id)})

        assert response.status_code == 201
        assert response.data["data"]["status"] == "ACTIVE"

        unit.refresh_from_db()
        assert unit.status == Unit.Status.OCCUPIED

        assert Occupancy.objects.filter(lease=lease, unit=unit).exists()

    def test_admin_can_activate_any_occupancy(self, authenticated_client):
        admin = AdminUserFactory()
        unit = UnitFactory(status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(admin)
        response = client.post("/api/occupancy/activate/", {"lease": str(lease.id)})

        assert response.status_code == 201

    def test_landlord_cannot_activate_occupancy_for_unowned_unit(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord_b), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord_a)
        response = client.post("/api/occupancy/activate/", {"lease": str(lease.id)})

        assert response.status_code == 403

        unit.refresh_from_db()
        assert unit.status == Unit.Status.VACANT  # untouched

    def test_cannot_activate_occupancy_for_non_active_lease(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ENDED)

        client = authenticated_client(landlord)
        response = client.post("/api/occupancy/activate/", {"lease": str(lease.id)})

        assert response.status_code == 400
        assert "lease" in response.data.get("errors", response.data)

    def test_cannot_activate_occupancy_twice_for_same_lease(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord)
        client.post("/api/occupancy/activate/", {"lease": str(lease.id)})
        response = client.post("/api/occupancy/activate/", {"lease": str(lease.id)})

        assert response.status_code == 400

    def test_cannot_activate_occupancy_on_already_occupied_unit(self, authenticated_client):
        """
        Simulates a unit that became OCCUPIED through some other path
        (defensive check even though Lease.clean() should normally
        prevent a second ACTIVE lease on the same unit first).
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.OCCUPIED)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord)
        response = client.post("/api/occupancy/activate/", {"lease": str(lease.id)})

        assert response.status_code == 400
        assert "unit" in response.data.get("errors", response.data)

    def test_move_in_date_defaults_to_today(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord)
        response = client.post("/api/occupancy/activate/", {"lease": str(lease.id)})

        assert response.data["data"]["move_in_date"] == str(date.today())

    def test_move_in_date_can_be_specified(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord)
        response = client.post(
            "/api/occupancy/activate/",
            {"lease": str(lease.id), "move_in_date": "2026-03-01"},
        )

        assert response.data["data"]["move_in_date"] == "2026-03-01"

    def test_tenant_cannot_activate_occupancy(self, authenticated_client):
        from apps.tenants.tests.factories import TenantFactory

        tenant_profile = TenantFactory()
        unit = UnitFactory(status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, tenant=tenant_profile, status=Lease.Status.ACTIVE)

        client = authenticated_client(tenant_profile.user)
        response = client.post("/api/occupancy/activate/", {"lease": str(lease.id)})

        assert response.status_code == 403