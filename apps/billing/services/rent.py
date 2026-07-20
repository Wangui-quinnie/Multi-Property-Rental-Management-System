from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.billing.models import BillingPeriod, Invoice, InvoiceItem
from apps.leases.models import Lease


def generate_invoice_number(lease, billing_period):
    return f"INV-{billing_period.start_date.strftime('%Y%m')}-{str(lease.id)[:8].upper()}"


def get_active_leases_for_user(user):
    """
    Scopes which active leases a user may generate rent invoices for.
    ADMIN: all active leases. LANDLORD: only leases on units they own.
    """
    queryset = Lease.objects.filter(
        status=Lease.Status.ACTIVE
    ).select_related("tenant", "unit", "unit__property")

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(unit__property__landlord=user)

    return queryset.none()


@transaction.atomic
def generate_rent_invoice_for_lease(lease, billing_period):
    if billing_period.status == BillingPeriod.Status.CLOSED:
        raise ValidationError(
            {"billing_period": "Cannot generate invoices for a CLOSED billing period."}
        )

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
def generate_monthly_rent_invoices(billing_period, user):
    """
    Generates (or refreshes) rent invoices for every active lease this
    user is allowed to bill. ADMIN generates system-wide; LANDLORD is
    scoped to leases on units they own. Idempotent — safe to re-run
    for the same billing period (get_or_create keyed on a deterministic
    invoice number).
    """
    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD):
        raise PermissionDenied(
            "Only Admin or Landlord can generate rent invoices."
        )

    active_leases = get_active_leases_for_user(user)

    created_invoices = []
    for lease in active_leases:
        invoice = generate_rent_invoice_for_lease(lease, billing_period)
        created_invoices.append(invoice)

    return created_invoices