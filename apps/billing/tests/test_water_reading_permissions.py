import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.billing.models import WaterMeterReading
from apps.billing.tests.factories import BillingPeriodFactory

pytestmark = pytest.mark.django_db


class TestWaterReadingPermissions:
    def test_landlord_creates_reading_for_own_unit(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        billing_period = BillingPeriodFactory()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/billing/water-readings/",
            {
                "unit": str(unit.id),
                "billing_period": str(billing_period.id),
                "previous_reading": "100.00",
                "current_reading": "150.00",
                "rate_per_unit": "50.00",
                "reading_date": "2026-01-31",
            },
        )

        assert response.status_code == 201
        assert WaterMeterReading.objects.filter(unit=unit).exists()

    def test_landlord_cannot_create_reading_for_unowned_unit(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord_b))
        billing_period = BillingPeriodFactory()

        client = authenticated_client(landlord_a)
        response = client.post(
            "/api/billing/water-readings/",
            {
                "unit": str(unit.id),
                "billing_period": str(billing_period.id),
                "previous_reading": "0",
                "current_reading": "10",
                "rate_per_unit": "50.00",
                "reading_date": "2026-01-31",
            },
        )

        assert response.status_code == 403

    def test_admin_can_create_reading_for_any_unit(self, authenticated_client):
        admin = AdminUserFactory()
        unit = UnitFactory()
        billing_period = BillingPeriodFactory()

        client = authenticated_client(admin)
        response = client.post(
            "/api/billing/water-readings/",
            {
                "unit": str(unit.id),
                "billing_period": str(billing_period.id),
                "previous_reading": "0",
                "current_reading": "20",
                "rate_per_unit": "50.00",
                "reading_date": "2026-01-31",
            },
        )

        assert response.status_code == 201

    def test_tenant_cannot_create_reading(self, authenticated_client):
        from apps.tenants.tests.factories import TenantFactory

        tenant_profile = TenantFactory()
        unit = UnitFactory()
        billing_period = BillingPeriodFactory()

        client = authenticated_client(tenant_profile.user)
        response = client.post(
            "/api/billing/water-readings/",
            {
                "unit": str(unit.id),
                "billing_period": str(billing_period.id),
                "previous_reading": "0",
                "current_reading": "10",
                "rate_per_unit": "50.00",
                "reading_date": "2026-01-31",
            },
        )

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/billing/water-readings/")
        assert response.status_code == 401

    def test_duplicate_reading_for_same_unit_and_period_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        billing_period = BillingPeriodFactory()

        client = authenticated_client(landlord)
        payload = {
            "unit": str(unit.id),
            "billing_period": str(billing_period.id),
            "previous_reading": "0",
            "current_reading": "10",
            "rate_per_unit": "50.00",
            "reading_date": "2026-01-31",
        }
        client.post("/api/billing/water-readings/", payload)
        response = client.post("/api/billing/water-readings/", payload)

        assert response.status_code == 400
        assert "billing_period" in response.data

    def test_current_reading_less_than_previous_rejected(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        billing_period = BillingPeriodFactory()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/billing/water-readings/",
            {
                "unit": str(unit.id),
                "billing_period": str(billing_period.id),
                "previous_reading": "100",
                "current_reading": "50",
                "rate_per_unit": "50.00",
                "reading_date": "2026-01-31",
            },
        )

        assert response.status_code == 400

    def test_landlord_sees_only_own_readings(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()

        unit_a = UnitFactory(property=PropertyFactory(landlord=landlord_a))
        unit_b = UnitFactory(property=PropertyFactory(landlord=landlord_b))

        WaterMeterReading.objects.create(
            unit=unit_a, billing_period=BillingPeriodFactory(),
            previous_reading=0, current_reading=10, rate_per_unit=50, reading_date="2026-01-31",
        )
        WaterMeterReading.objects.create(
            unit=unit_b, billing_period=BillingPeriodFactory(),
            previous_reading=0, current_reading=10, rate_per_unit=50, reading_date="2026-01-31",
        )

        client = authenticated_client(landlord_a)
        response = client.get("/api/billing/water-readings/")

        results = response.data["results"]
        assert len(results) == 1
        assert str(results[0]["unit"]) == str(unit_a.id)