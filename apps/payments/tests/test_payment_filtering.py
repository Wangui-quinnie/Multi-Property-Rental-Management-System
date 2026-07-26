# Covers the PaymentViewSet.filterset_fields fix - added so the frontend
# can show status/tenant/payment-method scoped views via a real query
# param (Phase 5, Payments UI) - same gap Lease/Occupancy/Invoice/etc had.
import pytest

from apps.accounts.tests.factories import AdminUserFactory
from apps.payments.models import Payment
from apps.payments.tests.factories import PaymentFactory
from apps.tenants.tests.factories import TenantFactory

pytestmark = pytest.mark.django_db


class TestPaymentFiltering:
    def test_filter_by_status(self, authenticated_client):
        admin = AdminUserFactory()
        confirmed = PaymentFactory(status=Payment.Status.CONFIRMED)
        PaymentFactory(status=Payment.Status.PENDING)

        client = authenticated_client(admin)
        response = client.get("/api/payments/?status=CONFIRMED")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(confirmed.id)

    def test_filter_by_tenant(self, authenticated_client):
        admin = AdminUserFactory()
        tenant = TenantFactory()
        payment = PaymentFactory(tenant=tenant)
        PaymentFactory()  # different tenant

        client = authenticated_client(admin)
        response = client.get(f"/api/payments/?tenant={tenant.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(payment.id)

    def test_filter_by_payment_method(self, authenticated_client):
        admin = AdminUserFactory()
        cash_payment = PaymentFactory(payment_method=Payment.Method.CASH)
        PaymentFactory(payment_method=Payment.Method.BANK_TRANSFER)

        client = authenticated_client(admin)
        response = client.get("/api/payments/?payment_method=CASH")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(cash_payment.id)
