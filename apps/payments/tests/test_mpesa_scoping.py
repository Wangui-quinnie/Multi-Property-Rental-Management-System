import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.payments.services import initiate_stk_push

pytestmark = pytest.mark.django_db


def _tenant_with_transaction(landlord=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
    txn = initiate_stk_push(
        tenant=lease.tenant, phone_number="254712345678", amount=5000, user=landlord
    )
    return txn, lease.tenant, landlord


class TestMpesaTransactionScoping:
    def test_landlord_sees_only_own_transactions(self, authenticated_client):
        txn_a, tenant_a, landlord_a = _tenant_with_transaction()
        _tenant_with_transaction()  # unrelated landlord

        client = authenticated_client(landlord_a)
        response = client.get("/api/payments/mpesa/transactions/")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(txn_a.id)

    def test_admin_sees_all_transactions(self, authenticated_client):
        admin = AdminUserFactory()
        _tenant_with_transaction()
        _tenant_with_transaction()

        client = authenticated_client(admin)
        response = client.get("/api/payments/mpesa/transactions/")

        assert len(response.data["results"]) == 2

    def test_tenant_sees_only_own_transaction(self, authenticated_client):
        txn, tenant, landlord = _tenant_with_transaction()

        client = authenticated_client(tenant.user)
        response = client.get("/api/payments/mpesa/transactions/")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(txn.id)

    def test_router_does_not_swallow_mpesa_transactions_path(self, authenticated_client):
        """
        Regression guard: 'mpesa/transactions/' must resolve to
        MpesaTransactionViewSet's list action, not get misrouted into
        PaymentViewSet's detail lookup (which would try to treat
        'mpesa' as a malformed payment pk and 404 or error).
        """
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)

        response = client.get("/api/payments/mpesa/transactions/")

        assert response.status_code == 200
        assert "results" in response.data  # confirms list-shaped response, not a detail 404

    def test_unauthenticated_list_rejected(self, api_client):
        response = api_client.get("/api/payments/mpesa/transactions/")
        assert response.status_code == 401