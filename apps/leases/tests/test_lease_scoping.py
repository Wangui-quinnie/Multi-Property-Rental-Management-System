import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.tenants.tests.factories import TenantFactory
from apps.leases.tests.factories import LeaseFactory

pytestmark = pytest.mark.django_db


class TestLeaseOwnershipScoping:
    def test_landlord_sees_only_leases_on_own_units(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()

        unit_a = UnitFactory(property=PropertyFactory(landlord=landlord_a))
        unit_b = UnitFactory(property=PropertyFactory(landlord=landlord_b))

        lease_a = LeaseFactory(unit=unit_a)
        LeaseFactory(unit=unit_b)

        client = authenticated_client(landlord_a)
        response = client.get("/api/leases/")

        assert response.status_code == 200
        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(lease_a.id)

    def test_admin_sees_all_leases(self, authenticated_client):
        admin = AdminUserFactory()
        LeaseFactory()
        LeaseFactory()

        client = authenticated_client(admin)
        response = client.get("/api/leases/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_tenant_sees_only_own_lease(self, authenticated_client):
        tenant_profile = TenantFactory()
        other_tenant_profile = TenantFactory()

        own_lease = LeaseFactory(tenant=tenant_profile)
        LeaseFactory(tenant=other_tenant_profile)

        client = authenticated_client(tenant_profile.user)
        response = client.get("/api/leases/")

        assert response.status_code == 200
        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(own_lease.id)

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/leases/")
        assert response.status_code == 401

    def test_landlord_cannot_retrieve_other_landlords_lease(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()

        other_lease = LeaseFactory(unit=UnitFactory(property=PropertyFactory(landlord=landlord_b)))

        client = authenticated_client(landlord_a)
        response = client.get(f"/api/leases/{other_lease.id}/")

        assert response.status_code == 404

    def test_tenant_cannot_retrieve_another_tenants_lease(self, authenticated_client):
        tenant_profile = TenantFactory()
        other_lease = LeaseFactory(tenant=TenantFactory())

        client = authenticated_client(tenant_profile.user)
        response = client.get(f"/api/leases/{other_lease.id}/")

        assert response.status_code == 404