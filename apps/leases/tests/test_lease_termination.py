import pytest
from datetime import date

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.properties.models import Unit
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.occupancy.services import activate_occupancy
from apps.occupancy.models import Occupancy

pytestmark = pytest.mark.django_db


class TestLeaseTermination:
    def test_landlord_terminates_lease_with_active_occupancy(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
        occupancy = activate_occupancy(lease=lease, user=landlord)

        unit.refresh_from_db()
        assert unit.status == Unit.Status.OCCUPIED

        client = authenticated_client(landlord)
        response = client.post(f"/api/leases/{lease.id}/terminate/", {})

        assert response.status_code == 200

        lease.refresh_from_db()
        assert lease.status == Lease.Status.ENDED

        occupancy.refresh_from_db()
        assert occupancy.status == Occupancy.Status.ENDED
        assert occupancy.move_out_date == date.today()

        unit.refresh_from_db()
        assert unit.status == Unit.Status.VACANT

    def test_terminate_lease_with_no_occupancy_yet(self, authenticated_client):
        """
        A lease can be ACTIVE before the tenant physically moves in
        (occupancy activation is a separate step). Terminating such a
        lease should succeed cleanly with nothing to revert.
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord)
        response = client.post(f"/api/leases/{lease.id}/terminate/", {})

        assert response.status_code == 200

        lease.refresh_from_db()
        assert lease.status == Lease.Status.ENDED

        unit.refresh_from_db()
        assert unit.status == Unit.Status.VACANT  # untouched, was already VACANT

        assert not Occupancy.objects.filter(lease=lease).exists()

    def test_admin_can_terminate_any_lease(self, authenticated_client):
        admin = AdminUserFactory()
        lease = LeaseFactory(status=Lease.Status.ACTIVE)

        client = authenticated_client(admin)
        response = client.post(f"/api/leases/{lease.id}/terminate/", {})

        assert response.status_code == 200

    def test_landlord_cannot_terminate_another_landlords_lease(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord_b))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        client = authenticated_client(landlord_a)
        response = client.post(f"/api/leases/{lease.id}/terminate/", {})

        # Blocked at queryset scoping (get_object) before the action body runs
        assert response.status_code == 404

        lease.refresh_from_db()
        assert lease.status == Lease.Status.ACTIVE  # untouched

    def test_tenant_cannot_terminate_lease(self, authenticated_client):
        tenant_profile = TenantFactory()
        lease = LeaseFactory(tenant=tenant_profile, status=Lease.Status.ACTIVE)

        client = authenticated_client(tenant_profile.user)
        response = client.post(f"/api/leases/{lease.id}/terminate/", {})

        assert response.status_code == 403

    def test_cannot_terminate_already_ended_lease(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ENDED)

        client = authenticated_client(landlord)
        response = client.post(f"/api/leases/{lease.id}/terminate/", {})

        assert response.status_code == 400

    def test_custom_termination_date_is_used(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
        occupancy = activate_occupancy(lease=lease, user=landlord)

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/leases/{lease.id}/terminate/",
            {"termination_date": "2026-08-15"},
        )

        assert response.status_code == 200

        lease.refresh_from_db()
        assert str(lease.lease_end_date) == "2026-08-15"

        occupancy.refresh_from_db()
        assert str(occupancy.move_out_date) == "2026-08-15"

    def test_lease_end_date_not_overwritten_if_earlier_than_termination(self, authenticated_client):
        """
        If the lease already had an earlier scheduled end date than
        the actual termination date, that earlier date should be
        preserved, not pushed later.
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date="2026-06-01")

        client = authenticated_client(landlord)
        client.post(
            f"/api/leases/{lease.id}/terminate/",
            {"termination_date": "2026-08-15"},  # later than existing end date
        )

        lease.refresh_from_db()
        assert str(lease.lease_end_date) == "2026-06-01"  # unchanged

    def test_lease_end_date_updated_if_terminated_early(self, authenticated_client):
        """
        If termination happens BEFORE the originally scheduled end
        date (early termination), lease_end_date should update to
        reflect reality.
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date="2027-06-01")

        client = authenticated_client(landlord)
        client.post(
            f"/api/leases/{lease.id}/terminate/",
            {"termination_date": "2026-08-15"},  # earlier than existing end date
        )

        lease.refresh_from_db()
        assert str(lease.lease_end_date) == "2026-08-15"

    def test_terminating_already_ended_occupancy_does_not_reprocess(self, authenticated_client):
        """
        Defensive check: if an Occupancy somehow already has
        status=ENDED before termination runs (edge case), termination
        should still succeed on the lease without erroring, and should
        not touch the already-ended occupancy or unit again.
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
        occupancy = activate_occupancy(lease=lease, user=landlord)

        occupancy.status = Occupancy.Status.ENDED
        occupancy.move_out_date = date(2026, 1, 1)
        occupancy.save()

        unit.status = Unit.Status.MAINTENANCE  # simulate unit moved on independently
        unit.save()

        client = authenticated_client(landlord)
        response = client.post(f"/api/leases/{lease.id}/terminate/", {})

        assert response.status_code == 200

        occupancy.refresh_from_db()
        assert occupancy.move_out_date == date(2026, 1, 1)  # untouched, not overwritten

        unit.refresh_from_db()
        assert unit.status == Unit.Status.MAINTENANCE  # untouched, termination didn't force VACANT