import pytest

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.tenants.tests.factories import TenantFactory
from apps.leases.tests.factories import LeaseFactory

pytestmark = pytest.mark.django_db


class TestLeasePermissions:
    def test_landlord_can_create_lease_on_own_unit(self, authenticated_client):
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
                "billing_day": 1,
            },
        )

        assert response.status_code == 201

    def test_landlord_cannot_create_lease_on_another_landlords_unit(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord_b))
        tenant_profile = TenantFactory()

        client = authenticated_client(landlord_a)
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

        assert response.status_code == 403

    def test_tenant_cannot_create_lease(self, authenticated_client):
        tenant_profile = TenantFactory()
        unit = UnitFactory()

        client = authenticated_client(tenant_profile.user)
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

        assert response.status_code == 403

    def test_tenant_cannot_update_own_lease(self, authenticated_client):
        tenant_profile = TenantFactory()
        lease = LeaseFactory(tenant=tenant_profile)

        client = authenticated_client(tenant_profile.user)
        response = client.patch(f"/api/leases/{lease.id}/", {"rent_amount": 99999})

        assert response.status_code == 403

    def test_delete_is_disabled_for_everyone(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease = LeaseFactory(unit=UnitFactory(property=PropertyFactory(landlord=landlord)))

        client = authenticated_client(landlord)
        response = client.delete(f"/api/leases/{lease.id}/")

        assert response.status_code == 405

    def test_landlord_can_update_lease_on_own_unit(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease = LeaseFactory(unit=UnitFactory(property=PropertyFactory(landlord=landlord)))

        client = authenticated_client(landlord)
        response = client.patch(f"/api/leases/{lease.id}/", {"rent_amount": 27000})

        assert response.status_code == 200
        lease.refresh_from_db()
        assert lease.rent_amount == 27000