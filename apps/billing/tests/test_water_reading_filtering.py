# Covers the WaterMeterReadingViewSet.filterset_fields fix - added so the
# frontend can scope the readings table to a specific billing period or
# unit via a real query param (Phase 4, Billing UI).
import pytest

from apps.accounts.tests.factories import AdminUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.billing.models import WaterMeterReading
from apps.billing.tests.factories import BillingPeriodFactory

pytestmark = pytest.mark.django_db


def _make_reading(unit=None, billing_period=None):
    unit = unit or UnitFactory()
    billing_period = billing_period or BillingPeriodFactory()
    return WaterMeterReading.objects.create(
        unit=unit,
        billing_period=billing_period,
        previous_reading=100,
        current_reading=150,
        rate_per_unit=50,
        reading_date="2026-01-31",
    )


class TestWaterReadingFiltering:
    def test_filter_by_billing_period(self, authenticated_client):
        admin = AdminUserFactory()
        billing_period = BillingPeriodFactory()

        reading = _make_reading(billing_period=billing_period)
        _make_reading(billing_period=BillingPeriodFactory())  # different period

        client = authenticated_client(admin)
        response = client.get(f"/api/billing/water-readings/?billing_period={billing_period.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(reading.id)

    def test_filter_by_unit(self, authenticated_client):
        admin = AdminUserFactory()
        unit = UnitFactory()

        reading = _make_reading(unit=unit)
        _make_reading()  # different unit

        client = authenticated_client(admin)
        response = client.get(f"/api/billing/water-readings/?unit={unit.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(reading.id)
