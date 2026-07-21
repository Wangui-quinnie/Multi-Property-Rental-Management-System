import pytest

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import Invoice, InvoiceItem, WaterMeterReading
from apps.billing.tests.factories import BillingPeriodFactory

pytestmark = pytest.mark.django_db


def _make_reading(landlord=None, units_consumed=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
    billing_period = BillingPeriodFactory()
    reading = WaterMeterReading.objects.create(
        unit=unit,
        billing_period=billing_period,
        previous_reading=100,
        current_reading=150,
        rate_per_unit=50,
        reading_date="2026-01-31",
    )
    return reading, landlord, lease


class TestWaterChargeApplication:
    def test_apply_charge_creates_invoice_and_item(self, authenticated_client):
        reading, landlord, lease = _make_reading()

        client = authenticated_client(landlord)
        response = client.post(f"/api/billing/water-readings/{reading.id}/apply-charge/")

        assert response.status_code == 201

        invoice = Invoice.objects.get(lease=lease, billing_period=reading.billing_period)
        water_item = invoice.items.get(item_type=InvoiceItem.ItemType.WATER)

        assert water_item.quantity == 50  # 150 - 100
        assert water_item.unit_price == 50
        assert water_item.amount == 2500  # 50 * 50

        reading.refresh_from_db()
        assert reading.invoice_item_id == water_item.id

    def test_reapplying_charge_does_not_duplicate(self, authenticated_client):
        reading, landlord, lease = _make_reading()

        client = authenticated_client(landlord)
        client.post(f"/api/billing/water-readings/{reading.id}/apply-charge/")
        client.post(f"/api/billing/water-readings/{reading.id}/apply-charge/")

        invoice = Invoice.objects.get(lease=lease, billing_period=reading.billing_period)
        assert invoice.items.filter(item_type=InvoiceItem.ItemType.WATER).count() == 1

    def test_apply_charge_adds_to_existing_rent_invoice(self, authenticated_client):
        """
        If a rent invoice already exists for this lease + billing
        period, the water charge should be added as another line item
        on the SAME invoice, not create a second one.
        """
        from apps.billing.services import generate_rent_invoice_for_lease

        reading, landlord, lease = _make_reading()
        rent_invoice = generate_rent_invoice_for_lease(lease, reading.billing_period)

        client = authenticated_client(landlord)
        client.post(f"/api/billing/water-readings/{reading.id}/apply-charge/")

        assert Invoice.objects.filter(lease=lease, billing_period=reading.billing_period).count() == 1
        rent_invoice.refresh_from_db()
        assert rent_invoice.items.count() == 2  # RENT + WATER
        assert float(rent_invoice.total_amount) == float(lease.rent_amount) + 2500.0

    def test_landlord_cannot_apply_charge_for_unowned_unit(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        reading, landlord_b, lease = _make_reading()

        client = authenticated_client(landlord_a)
        response = client.post(f"/api/billing/water-readings/{reading.id}/apply-charge/")

        assert response.status_code == 404  # blocked at queryset scoping before reaching the action

    # apps/billing/tests/test_water_charge.py — inside test_correcting_billed_reading_updates_invoice_item
    def test_correcting_billed_reading_updates_invoice_item(self, authenticated_client):
        reading, landlord, lease = _make_reading()

        client = authenticated_client(landlord)
        client.post(f"/api/billing/water-readings/{reading.id}/apply-charge/")

        response = client.patch(
            f"/api/billing/water-readings/{reading.id}/",
            {"current_reading": "180"},  # corrected from 150 to 180
        )

        assert response.status_code == 200

        reading.refresh_from_db()
        assert reading.units_consumed == 80  # 180 - 100
        assert reading.amount == 4000  # 80 * 50

        water_item = reading.invoice_item
        water_item.refresh_from_db()
        assert water_item.quantity == 80
        assert water_item.amount == 4000

        invoice = water_item.invoice
        invoice.refresh_from_db()
        # Invoice also contains the auto-generated RENT item (lease.rent_amount),
        # since apply-charge creates the invoice if none existed yet.
        assert float(invoice.total_amount) == float(lease.rent_amount) + 4000.0

    def test_correcting_unbilled_reading_does_not_touch_invoice(self, authenticated_client):
        reading, landlord, lease = _make_reading()

        client = authenticated_client(landlord)
        response = client.patch(
            f"/api/billing/water-readings/{reading.id}/",
            {"current_reading": "200"},
        )

        assert response.status_code == 200
        reading.refresh_from_db()
        assert reading.units_consumed == 100  # 200 - 100
        assert reading.invoice_item_id is None

    def test_deleting_billed_reading_rejected(self, authenticated_client):
        reading, landlord, lease = _make_reading()

        client = authenticated_client(landlord)
        client.post(f"/api/billing/water-readings/{reading.id}/apply-charge/")

        response = client.delete(f"/api/billing/water-readings/{reading.id}/")

        assert response.status_code == 400
        assert WaterMeterReading.objects.filter(id=reading.id).exists()

    def test_deleting_unbilled_reading_succeeds(self, authenticated_client):
        reading, landlord, lease = _make_reading()

        client = authenticated_client(landlord)
        response = client.delete(f"/api/billing/water-readings/{reading.id}/")

        assert response.status_code == 204
        assert not WaterMeterReading.objects.filter(id=reading.id).exists()