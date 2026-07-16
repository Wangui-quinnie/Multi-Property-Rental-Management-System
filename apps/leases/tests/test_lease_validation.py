import pytest

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.tenants.tests.factories import TenantFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory

pytestmark = pytest.mark.django_db


class TestLeaseValidation:
    def test_cannot_create_second_active_lease_on_same_unit(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        tenant_profile = TenantFactory()
        client = authenticated_client(landlord)
        response = client.post(
            "/api/leases/",
            {
                "tenant": str(tenant_profile.id),
                "unit": str(unit.id),
                "lease_start_date": "2026-02-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 400

    def test_second_lease_allowed_if_first_is_ended(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        LeaseFactory(unit=unit, status=Lease.Status.ENDED)

        tenant_profile = TenantFactory()
        client = authenticated_client(landlord)
        response = client.post(
            "/api/leases/",
            {
                "tenant": str(tenant_profile.id),
                "unit": str(unit.id),
                "lease_start_date": "2026-02-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 201

    def test_end_date_before_start_date_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        tenant_profile = TenantFactory()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/leases/",
            {
                "tenant": str(tenant_profile.id),
                "unit": str(unit.id),
                "lease_start_date": "2026-06-01",
                "lease_end_date": "2026-01-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        assert response.status_code == 400

    def test_billing_day_out_of_range_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        tenant_profile = TenantFactory()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/leases/",
            {
                "tenant": str(tenant_profile.id),
                "unit": str(unit.id),
                "lease_start_date": "2026-02-01",
                "rent_amount": 20000,
                "billing_day": 45,
            },
        )

        assert response.status_code == 400

    def test_update_revalidates_business_rules(self, authenticated_client):
        """
        Ensures LeaseUpdateSerializer's validate() correctly falls back
        to the existing instance's unit/tenant/dates when checking
        rules, not just the fields being patched.
        """
        landlord = LandlordUserFactory()
        lease = LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord)),
            lease_start_date="2026-01-01",
        )

        client = authenticated_client(landlord)
        response = client.patch(
            f"/api/leases/{lease.id}/",
            {"lease_end_date": "2025-01-01"},  # before the existing start date
        )

        assert response.status_code == 400

    def test_creating_lease_does_not_change_unit_status(self, authenticated_client):
        """
        Confirms the deliberate design decision: Lease and Unit Occupancy
        are separate workflow steps. Creating a lease must not silently
        flip Unit.status to OCCUPIED.
        """
        from apps.properties.models import Unit

        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        tenant_profile = TenantFactory()

        client = authenticated_client(landlord)
        client.post(
            "/api/leases/",
            {
                "tenant": str(tenant_profile.id),
                "unit": str(unit.id),
                "lease_start_date": "2026-02-01",
                "rent_amount": 20000,
                "billing_day": 1,
            },
        )

        unit.refresh_from_db()
        assert unit.status == Unit.Status.VACANT