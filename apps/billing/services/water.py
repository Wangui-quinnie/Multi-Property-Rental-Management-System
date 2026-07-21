from django.db import transaction

from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.billing.models import Invoice, InvoiceItem
from apps.leases.models import Lease

from .rent import generate_rent_invoice_for_lease


def assert_landlord_owns_unit(*, unit, user):
    if user.role == user.Role.LANDLORD and unit.property.landlord != user:
        raise PermissionDenied(
            "You cannot manage water readings for a unit you don't own."
        )


def create_water_reading(*, serializer, user):
    unit = serializer.validated_data["unit"]
    assert_landlord_owns_unit(unit=unit, user=user)
    serializer.save()


def update_water_reading(*, serializer):
    """
    Saves the corrected reading (units_consumed/amount recompute
    automatically via WaterMeterReading.save()). If this reading was
    already billed, resyncs the linked InvoiceItem so the invoice
    immediately reflects the correction rather than staying stale.
    """
    with transaction.atomic():
        water_reading = serializer.save()

        if water_reading.invoice_item_id:
            item = water_reading.invoice_item
            item.quantity = water_reading.units_consumed
            item.unit_price = water_reading.rate_per_unit
            item.save()  # InvoiceItem.save() recomputes amount + calls invoice.refresh_totals()

    return water_reading


def delete_water_reading(*, water_reading):
    if water_reading.invoice_item_id:
        raise ValidationError(
            "Cannot delete a water reading that has already been billed. "
            "Correct it instead, or remove the associated invoice item first."
        )
    water_reading.delete()


@transaction.atomic
def add_water_charge_to_invoice(water_reading):
    lease = Lease.objects.filter(
        unit=water_reading.unit,
        status=Lease.Status.ACTIVE
    ).first()

    if not lease:
        raise ValueError("No active lease found for this unit.")

    invoice = Invoice.objects.filter(
        lease=lease,
        billing_period=water_reading.billing_period
    ).first()

    if not invoice:
        invoice = generate_rent_invoice_for_lease(
            lease=lease,
            billing_period=water_reading.billing_period
        )

    if water_reading.invoice_item:
        return water_reading.invoice_item

    invoice_item = InvoiceItem.objects.create(
        invoice=invoice,
        item_type=InvoiceItem.ItemType.WATER,
        description=f"Water bill for {water_reading.billing_period.name}",
        quantity=water_reading.units_consumed,
        unit_price=water_reading.rate_per_unit,
    )

    water_reading.invoice_item = invoice_item
    water_reading.save(update_fields=["invoice_item", "updated_at"])

    invoice.refresh_totals()
    return invoice_item


def apply_water_charge(*, water_reading, user):
    assert_landlord_owns_unit(unit=water_reading.unit, user=user)
    return add_water_charge_to_invoice(water_reading)