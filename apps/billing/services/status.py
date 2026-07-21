from rest_framework.exceptions import PermissionDenied

from ..models import Invoice


def mark_overdue_invoices(*, user):
    """
    Batch-persists status=OVERDUE for every UNPAID/PARTIALLY_PAID
    invoice this user can see whose due date has passed with a
    remaining balance. Scoped identically to invoice visibility
    (Admin all, Landlord own leases) — Tenant blocked entirely.

    This is a catch-up operation: refresh_totals() already keeps
    OVERDUE accurate automatically whenever an invoice's line items
    change, so this mainly matters for invoices nobody has touched
    since their due date passed.
    """
    from ..selectors import get_invoices_for_user

    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD):
        raise PermissionDenied(
            "Only Admin or Landlord can mark invoices overdue."
        )

    candidates = get_invoices_for_user(user).filter(
        status__in=[Invoice.Status.UNPAID, Invoice.Status.PARTIALLY_PAID]
    )

    updated_count = 0
    for invoice in candidates:
        if invoice.is_currently_overdue():
            invoice.status = Invoice.Status.OVERDUE
            invoice.save(update_fields=["status", "updated_at"])
            updated_count += 1

    return updated_count