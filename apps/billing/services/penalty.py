from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.billing.models import Invoice, InvoiceItem


def is_invoice_overdue(invoice):
    return invoice.due_date < date.today() and invoice.balance > 0


def calculate_late_fee_amount(*, invoice, fee_type, value):
    value = Decimal(str(value))

    if fee_type == "FIXED":
        return value

    if fee_type == "PERCENTAGE":
        return (invoice.balance * value / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    raise ValidationError({"fee_type": "fee_type must be FIXED or PERCENTAGE."})

def assert_can_manage_invoice(*, invoice, user):
    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD):
        raise PermissionDenied(
            "Only Admin or Landlord can apply late fees."
        )
    if user.role == user.Role.LANDLORD and invoice.lease.unit.property.landlord != user:
        raise PermissionDenied(
            "You cannot apply a late fee to an invoice you don't own."
        )

def apply_late_fee(*, invoice, user, fee_type, value):
    assert_can_manage_invoice(invoice=invoice, user=user)

    if not is_invoice_overdue(invoice):
        raise ValidationError(
            {"invoice": "Late fees can only be applied to overdue invoices with an outstanding balance."}
        )

    today_tag = f"Late fee applied {date.today()}"
    if InvoiceItem.objects.filter(
        invoice=invoice, item_type=InvoiceItem.ItemType.PENALTY, description=today_tag
    ).exists():
        raise ValidationError(
            {"invoice": "A late fee has already been applied to this invoice today."}
        )

    amount = calculate_late_fee_amount(invoice=invoice, fee_type=fee_type, value=value)

    item = InvoiceItem.objects.create(
        invoice=invoice,
        item_type=InvoiceItem.ItemType.PENALTY,
        description=today_tag,
        quantity=Decimal("1.00"),
        unit_price=amount,
    )
    # InvoiceItem.save() already calls invoice.refresh_totals()
    return item


def get_overdue_invoices_for_user(user):
    from .rent import get_active_leases_for_user

    leases = get_active_leases_for_user(user).values_list("id", flat=True)
    return [
        invoice for invoice in Invoice.objects.filter(lease_id__in=leases)
        if is_invoice_overdue(invoice)
    ]


def apply_late_fees_for_billing_period(*, billing_period, user, fee_type, value):
    """
    Applies a late fee to every overdue invoice in this billing period
    that the user can see. Invoices that already got a fee today are
    silently skipped (not treated as an error) — this is a batch
    operation, individual duplicates shouldn't abort the whole run.
    """
    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD):
        raise PermissionDenied(
            "Only Admin or Landlord can apply late fees."
        )

    candidates = get_overdue_invoices_for_user(user)
    candidates = [inv for inv in candidates if inv.billing_period_id == billing_period.id]

    applied_items = []
    for invoice in candidates:
        try:
            item = apply_late_fee(invoice=invoice, user=user, fee_type=fee_type, value=value)
            applied_items.append(item)
        except ValidationError:
            continue  # already fee'd today — skip, don't abort the batch

    return applied_items