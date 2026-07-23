import pytest
from datetime import datetime

from django.utils import timezone

from apps.accounts.tests.factories import LandlordUserFactory, TenantUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.payments.models import Payment
from apps.payments.tests.factories import PaymentFactory

pytestmark = pytest.mark.django_db


class TestCashFlowReport:
    def test_payments_grouped_by_month(self, authenticated_client):
        from apps.properties.tests.factories import PropertyFactory, UnitFactory
        from apps.leases.models import Lease
        from apps.leases.tests.factories import LeaseFactory

        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        PaymentFactory(
            tenant=lease.tenant, amount=10000,
            payment_date=timezone.make_aware(datetime(2026, 5, 10)),
            status=Payment.Status.CONFIRMED,
        )
        PaymentFactory(
            tenant=lease.tenant, amount=15000,
            payment_date=timezone.make_aware(datetime(2026, 5, 20)),
            status=Payment.Status.CONFIRMED,
        )
        PaymentFactory(
            tenant=lease.tenant, amount=8000,
            payment_date=timezone.make_aware(datetime(2026, 6, 5)),
            status=Payment.Status.CONFIRMED,
        )

        client = authenticated_client(landlord)
        response = client.get("/api/reports/cash-flow/?months=12")

        assert response.status_code == 200
        entries = {e["month"]: float(e["total_collected"]) for e in response.data["data"]}
        assert entries["2026-05"] == 25000.0
        assert entries["2026-06"] == 8000.0

    def test_pending_payments_excluded_from_cash_flow(self, authenticated_client):
        from apps.properties.tests.factories import PropertyFactory, UnitFactory
        from apps.leases.models import Lease
        from apps.leases.tests.factories import LeaseFactory

        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        PaymentFactory(
            tenant=lease.tenant, amount=10000,
            payment_date=timezone.now(), status=Payment.Status.PENDING,
        )

        client = authenticated_client(landlord)
        response = client.get("/api/reports/cash-flow/")

        assert response.data["data"] == []

    def test_tenant_cannot_access_cash_flow(self, authenticated_client):
        tenant = TenantUserFactory()

        client = authenticated_client(tenant)
        response = client.get("/api/reports/cash-flow/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/reports/cash-flow/")
        assert response.status_code == 401