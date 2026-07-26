# Covers the OccupancyViewSet.filterset_fields fix - added so the
# frontend can check "does this lease already have an occupancy?" via
# ?lease=<id> instead of guessing client-side (Phase 3, Lease UI).
import pytest

from apps.accounts.tests.factories import AdminUserFactory
from apps.properties.models import Unit
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.occupancy.services import activate_occupancy

pytestmark = pytest.mark.django_db


class TestOccupancyFiltering:
    def test_filter_by_lease_returns_only_that_leases_occupancy(self, authenticated_client):
        admin = AdminUserFactory()

        unit_a = UnitFactory(property=PropertyFactory(), status=Unit.Status.VACANT)
        lease_a = LeaseFactory(unit=unit_a, status=Lease.Status.ACTIVE)
        occupancy_a = activate_occupancy(lease=lease_a, user=admin)

        unit_b = UnitFactory(property=PropertyFactory(), status=Unit.Status.VACANT)
        lease_b = LeaseFactory(unit=unit_b, status=Lease.Status.ACTIVE)
        activate_occupancy(lease=lease_b, user=admin)

        client = authenticated_client(admin)
        response = client.get(f"/api/occupancy/?lease={lease_a.id}")

        assert response.status_code == 200
        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(occupancy_a.id)

    def test_filter_by_unit(self, authenticated_client):
        admin = AdminUserFactory()

        unit = UnitFactory(property=PropertyFactory(), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
        occupancy = activate_occupancy(lease=lease, user=admin)

        UnitFactory(property=PropertyFactory(), status=Unit.Status.VACANT)  # unrelated, no occupancy

        client = authenticated_client(admin)
        response = client.get(f"/api/occupancy/?unit={unit.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(occupancy.id)

    def test_filter_by_lease_with_no_occupancy_returns_empty(self, authenticated_client):
        admin = AdminUserFactory()
        unit = UnitFactory(property=PropertyFactory(), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)  # never activated

        client = authenticated_client(admin)
        response = client.get(f"/api/occupancy/?lease={lease.id}")

        assert response.data["results"] == []