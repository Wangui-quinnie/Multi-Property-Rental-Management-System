# Covers the BillingPeriodViewSet.filterset_fields fix - added so the
# frontend can restrict a "generate rent invoices" period picker to OPEN
# periods only via ?status=OPEN (Phase 4, Billing UI).
import pytest

from apps.accounts.tests.factories import AdminUserFactory
from apps.billing.models import BillingPeriod
from apps.billing.tests.factories import BillingPeriodFactory

pytestmark = pytest.mark.django_db


class TestBillingPeriodFiltering:
    def test_filter_by_status(self, authenticated_client):
        admin = AdminUserFactory()
        open_period = BillingPeriodFactory(status=BillingPeriod.Status.OPEN)
        BillingPeriodFactory(status=BillingPeriod.Status.CLOSED)

        client = authenticated_client(admin)
        response = client.get("/api/billing/periods/?status=OPEN")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(open_period.id)
