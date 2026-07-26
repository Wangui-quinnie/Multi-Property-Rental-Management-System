# Covers the MpesaTransactionViewSet.filterset_fields fix - added so the
# frontend can scope the transactions table to a status or tenant via a
# real query param (Phase 5, Payments UI).
import pytest

from apps.accounts.tests.factories import AdminUserFactory
from apps.payments.models import MpesaTransaction
from apps.payments.services import initiate_stk_push, process_stk_callback
from apps.tenants.tests.factories import TenantFactory

pytestmark = pytest.mark.django_db


class TestMpesaTransactionFiltering:
    def test_filter_by_status(self, authenticated_client):
        admin = AdminUserFactory()

        pending_tenant = TenantFactory()
        pending_txn = initiate_stk_push(
            tenant=pending_tenant, phone_number="254712345678", amount=1000, user=admin
        )

        success_tenant = TenantFactory()
        success_txn = initiate_stk_push(
            tenant=success_tenant, phone_number="254712345679", amount=2000, user=admin
        )
        process_stk_callback(
            checkout_request_id=success_txn.checkout_request_id,
            result_code=0,
            result_description="Success",
            mpesa_receipt_number="ABC123",
        )

        client = authenticated_client(admin)
        response = client.get("/api/payments/mpesa/transactions/?status=PENDING")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(pending_txn.id)

    def test_filter_by_tenant(self, authenticated_client):
        admin = AdminUserFactory()
        tenant = TenantFactory()
        txn = initiate_stk_push(tenant=tenant, phone_number="254712345678", amount=1000, user=admin)
        initiate_stk_push(tenant=TenantFactory(), phone_number="254712345679", amount=2000, user=admin)

        client = authenticated_client(admin)
        response = client.get(f"/api/payments/mpesa/transactions/?tenant={tenant.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(txn.id)
