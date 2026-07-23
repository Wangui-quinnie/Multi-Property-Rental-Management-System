import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.billing.models import WaterMeterReading
from apps.billing.tests.factories import BillingPeriodFactory

pytestmark = pytest.mark.django_db


def _make_reading(landlord=None, consumed=50, rate=50, reading_date=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    billing_period = BillingPeriodFactory()
    reading = WaterMeterReading.objects.create(
        unit=unit,
        billing_period=billing_period,
        previous_reading=0,
        current_reading=consumed,
        rate_per_unit=rate,
        reading_date=reading_date or date.today(),
    )
    return reading, landlord


class TestWaterReport:
    def test_water_totals_match_readings(self, authenticated_client):
        reading, landlord = _make_reading(consumed=50, rate=50)

        client = authenticated_client(landlord)
        response = client.get("/api/reports/water/")

        assert response.status_code == 200
        data = response.data["data"]
        assert float(data["total_units_consumed"]) == 50.0
        assert float(data["total_water_billed"]) == 2500.0
        assert data["reading_count"] == 1

    def test_multiple_readings_sum_correctly(self, authenticated_client):
        landlord = LandlordUserFactory()
        _make_reading(landlord=landlord, consumed=30, rate=50)
        _make_reading(landlord=landlord, consumed=20, rate=50)

        client = authenticated_client(landlord)
        response = client.get("/api/reports/water/")

        data = response.data["data"]
        assert float(data["total_units_consumed"]) == 50.0
        assert data["reading_count"] == 2

    def test_date_filtering_narrows_results(self, authenticated_client):
        landlord = LandlordUserFactory()
        _make_reading(landlord=landlord, consumed=30, rate=50, reading_date=date(2025, 3, 1))
        _make_reading(landlord=landlord, consumed=40, rate=50, reading_date=date(2026, 6, 1))

        client = authenticated_client(landlord)
        response = client.get("/api/reports/water/?start_date=2026-01-01&end_date=2026-12-31")

        data = response.data["data"]
        assert data["reading_count"] == 1
        assert float(data["total_units_consumed"]) == 40.0

    def test_landlord_sees_only_own_water_data(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        _make_reading(landlord=landlord_a, consumed=20, rate=50)
        _make_reading(consumed=999, rate=50)  # unrelated landlord

        client = authenticated_client(landlord_a)
        response = client.get("/api/reports/water/")

        assert float(response.data["data"]["total_units_consumed"]) == 20.0

    def test_admin_sees_all_water_data(self, authenticated_client):
        admin = AdminUserFactory()
        _make_reading(consumed=20, rate=50)
        _make_reading(consumed=30, rate=50)

        client = authenticated_client(admin)
        response = client.get("/api/reports/water/")

        assert response.data["data"]["reading_count"] == 2

    def test_tenant_cannot_access_water_report(self, authenticated_client):
        tenant = TenantUserFactory()

        client = authenticated_client(tenant)
        response = client.get("/api/reports/water/")

        assert response.status_code == 403

    def test_zero_readings_no_crash(self, authenticated_client):
        landlord = LandlordUserFactory()

        client = authenticated_client(landlord)
        response = client.get("/api/reports/water/")

        assert response.status_code == 200
        data = response.data["data"]
        assert float(data["total_units_consumed"]) == 0.0
        assert data["reading_count"] == 0