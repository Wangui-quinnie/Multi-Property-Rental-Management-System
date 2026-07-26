# Covers the LeaseViewSet.filterset_fields fix - added so the frontend
# can show status tabs (Active/Ended/Cancelled) and unit/tenant-scoped
# views via a real query param (Phase 3, Lease UI).
import pytest

from apps.accounts.tests.factories import AdminUserFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory

pytestmark = pytest.mark.django_db


class TestLeaseFiltering:
    def test_filter_by_status(self, authenticated_client):
        admin = AdminUserFactory()
        active_lease = LeaseFactory(status=Lease.Status.ACTIVE)
        LeaseFactory(status=Lease.Status.ENDED)
        LeaseFactory(status=Lease.Status.CANCELLED)

        client = authenticated_client(admin)
        response = client.get("/api/leases/?status=ACTIVE")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(active_lease.id)

    def test_filter_by_unit(self, authenticated_client):
        admin = AdminUserFactory()
        lease = LeaseFactory()
        LeaseFactory()  # unrelated unit

        client = authenticated_client(admin)
        response = client.get(f"/api/leases/?unit={lease.unit.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(lease.id)

    def test_filter_by_tenant(self, authenticated_client):
        admin = AdminUserFactory()
        lease = LeaseFactory()
        LeaseFactory()  # unrelated tenant

        client = authenticated_client(admin)
        response = client.get(f"/api/leases/?tenant={lease.tenant.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(lease.id)