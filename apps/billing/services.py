from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.billing.models import BillingPeriod, Invoice, InvoiceItem, WaterMeterReading
from apps.leases.models import Lease


def generate_invoice_number(lease, billing_period):
    return f"INV-{billing_period.start_date.strftime('%Y%m')}-{str(lease.id)[:8].upper()}"


@transaction.atomic
def generate_rent_invoice_for_lease(lease, billing_period):
    invoice_number = generate_invoice_number(lease, billing_period)

    invoice, created = Invoice.objects.get_or_create(
        lease=lease,
        billing_period=billing_period,
        invoice_number=invoice_number,
        defaults={
            "invoice_date": timezone.now().date(),
            "due_date": billing_period.due_date,
            "status": Invoice.Status.UNPAID,
        }
    )

    if created:
        InvoiceItem.objects.create(
            invoice=invoice,
            item_type=InvoiceItem.ItemType.RENT,
            description=f"Rent for {billing_period.name}",
            quantity=Decimal("1.00"),
            unit_price=lease.rent_amount,
        )

    invoice.refresh_totals()
    return invoice


@transaction.atomic
def generate_monthly_rent_invoices(billing_period):
    active_leases = Lease.objects.filter(
        status=Lease.Status.ACTIVE
    ).select_related(
        "tenant",
        "unit",
        "unit__property",
    )

    created_invoices = []

    for lease in active_leases:
        invoice = generate_rent_invoice_for_lease(lease, billing_period)
        created_invoices.append(invoice)

    return created_invoices


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