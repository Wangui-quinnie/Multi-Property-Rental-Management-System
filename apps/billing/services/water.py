from django.db import transaction

from apps.billing.models import Invoice, InvoiceItem
from apps.leases.models import Lease

from .rent import generate_rent_invoice_for_lease


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