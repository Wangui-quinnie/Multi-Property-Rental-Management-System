import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.properties.models import Unit
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.occupancy.services import activate_occupancy

pytestmark = pytest.mark.django_db


def _make_active_occupancy(landlord=None, tenant_profile=None):
    landlord = landlord or LandlordUserFactory()
    tenant_profile = tenant_profile or TenantFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
    lease = LeaseFactory(unit=unit, tenant=tenant_profile, status=Lease.Status.ACTIVE)
    occupancy = activate_occupancy(lease=lease, user=landlord)
    return occupancy, landlord, tenant_profile


class TestOccupancyScoping:
    def test_landlord_sees_only_own_occupancies(self, authenticated_client):
        occupancy_a, landlord_a, _ = _make_active_occupancy()
        _make_active_occupancy()  # unrelated landlord

        client = authenticated_client(landlord_a)
        response = client.get("/api/occupancy/")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(occupancy_a.id)

    def test_admin_sees_all_occupancies(self, authenticated_client):
        admin = AdminUserFactory()
        _make_active_occupancy()
        _make_active_occupancy()

        client = authenticated_client(admin)
        response = client.get("/api/occupancy/")

        assert len(response.data["results"]) == 2

    def test_tenant_sees_only_own_occupancy(self, authenticated_client):
        occupancy, _, tenant_profile = _make_active_occupancy()
        _make_active_occupancy()  # unrelated tenant

        client = authenticated_client(tenant_profile.user)
        response = client.get("/api/occupancy/")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(occupancy.id)

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/occupancy/")
        assert response.status_code == 401

    def test_write_methods_not_exposed_on_list_endpoint(self, authenticated_client):
        """
        Confirms ReadOnlyBaseViewSet actually blocks POST/PUT/DELETE
        on the standard collection endpoint — the only valid write
        path is the dedicated /activate/ action.
        """
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)

        response = client.post("/api/occupancy/", {"lease": "some-id"})
        assert response.status_code == 405