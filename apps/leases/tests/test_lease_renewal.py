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


class TestLeaseRenewal:
    def test_landlord_renews_own_active_lease(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        old_lease = LeaseFactory(
            unit=unit,
            status=Lease.Status.ACTIVE,
            lease_start_date="2026-01-01",
            lease_end_date="2026-12-31",
        )

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2027-01-01",
                "new_lease_end_date": "2027-12-31",
                "rent_amount": 27000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 201

        old_lease.refresh_from_db()
        assert old_lease.status == Lease.Status.ENDED

        new_lease_id = response.data["data"]["id"]
        new_lease = Lease.objects.get(id=new_lease_id)
        assert new_lease.status == Lease.Status.ACTIVE
        assert new_lease.renewed_from_id == old_lease.id
        assert new_lease.tenant_id == old_lease.tenant_id
        assert new_lease.unit_id == old_lease.unit_id
        assert new_lease.rent_amount == 27000

    def test_admin_can_renew_any_lease(self, authenticated_client):
        admin = AdminUserFactory()
        old_lease = LeaseFactory(status=Lease.Status.ACTIVE, lease_end_date="2026-12-31")

        client = authenticated_client(admin)
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2027-01-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 201

    def test_landlord_cannot_renew_another_landlords_lease(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord_b))
        old_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date="2026-12-31")

        client = authenticated_client(landlord_a)
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2027-01-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        # Blocked at queryset scoping (get_object) before the action body runs
        assert response.status_code == 404

        old_lease.refresh_from_db()
        assert old_lease.status == Lease.Status.ACTIVE  # untouched

    def test_tenant_cannot_renew_lease(self, authenticated_client):
        tenant_profile = TenantFactory()
        old_lease = LeaseFactory(tenant=tenant_profile, status=Lease.Status.ACTIVE, lease_end_date="2026-12-31")

        client = authenticated_client(tenant_profile.user)
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2027-01-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 403

    def test_cannot_renew_already_ended_lease(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        old_lease = LeaseFactory(unit=unit, status=Lease.Status.ENDED, lease_end_date="2026-12-31")

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2027-01-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 400

    def test_cannot_renew_already_renewed_lease(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        old_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date="2026-12-31")

        client = authenticated_client(landlord)
        client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {"new_lease_start_date": "2027-01-01", "rent_amount": 20000, "billing_day": 1},
        )

        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {"new_lease_start_date": "2028-01-01", "rent_amount": 21000, "billing_day": 1},
        )

        assert response.status_code == 400

    def test_new_start_date_before_old_end_date_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        old_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date="2026-12-31")

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2026-06-01",  # before old lease ends
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 400

    def test_renewal_does_not_touch_occupancy_or_unit_status(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        old_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date="2026-12-31")

        occupancy = activate_occupancy(lease=old_lease, user=landlord)
        unit.refresh_from_db()
        assert unit.status == Unit.Status.OCCUPIED

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2027-01-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 201

        unit.refresh_from_db()
        assert unit.status == Unit.Status.OCCUPIED  # unchanged by renewal

        occupancy.refresh_from_db()
        assert occupancy.lease_id == old_lease.id  # still points at the OLD lease
        assert occupancy.status == Occupancy.Status.ACTIVE  # untouched

    def test_old_lease_end_date_set_if_missing(self, authenticated_client):
        """
        If the original lease had no end date (open-ended/rolling
        lease), renewing it should backfill lease_end_date to the new
        lease's start date rather than leaving it null.
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        old_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2027-01-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 201
        old_lease.refresh_from_db()
        assert str(old_lease.lease_end_date) == "2027-01-01"

    def test_renewal_is_atomic_on_new_lease_validation_failure(self, authenticated_client):
        """
        If the new lease fails Lease.clean() validation (e.g. invalid
        billing_day slipping past the serializer somehow), the OLD
        lease must NOT have been marked ENDED — the whole operation
        should roll back together.
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        old_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date="2026-12-31")

        client = authenticated_client(landlord)
        # end date before start date on the NEW lease -> should fail Lease.clean()
        response = client.post(
            f"/api/leases/{old_lease.id}/renew/",
            {
                "new_lease_start_date": "2027-06-01",
                "new_lease_end_date": "2027-01-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 400

        old_lease.refresh_from_db()
        assert old_lease.status == Lease.Status.ACTIVE  # rollback confirmed