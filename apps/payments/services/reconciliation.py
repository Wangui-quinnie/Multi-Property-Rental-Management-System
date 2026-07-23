from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from ..models import Payment, MpesaTransaction
from ..selectors import get_payments_for_user, get_mpesa_transactions_for_user
from .payment import assert_landlord_manages_tenant

STALE_PENDING_THRESHOLD = timedelta(hours=1)


def get_unallocated_payments(user):
    """
    CONFIRMED payments where the sum of allocations is less than the
    payment amount — money received but not (fully) applied.
    """
    payments = get_payments_for_user(user).filter(status=Payment.Status.CONFIRMED)

    unallocated = []
    for payment in payments:
        total_allocated = payment.allocations.aggregate(total=Sum("amount_allocated"))["total"] or Decimal("0")
        if total_allocated < payment.amount:
            unallocated.append({
                "payment_id": str(payment.id),
                "payment_reference": payment.payment_reference,
                "tenant_name": payment.tenant.user.get_full_name(),
                "amount": payment.amount,
                "total_allocated": total_allocated,
                "unallocated_amount": payment.amount - total_allocated,
            })

    return unallocated


def get_stale_pending_mpesa_transactions(user):
    """
    STK Push transactions stuck in PENDING longer than the threshold —
    the callback likely never arrived, or the customer abandoned the
    prompt. These need manual follow-up (contact tenant, check
    Safaricom's transaction status API in a real deployment).
    """
    cutoff = timezone.now() - STALE_PENDING_THRESHOLD

    transactions = get_mpesa_transactions_for_user(user).filter(
        status=MpesaTransaction.Status.PENDING,
        created_at__lt=cutoff,
    )

    return [
        {
            "transaction_id": str(txn.id),
            "checkout_request_id": txn.checkout_request_id,
            "tenant_name": txn.tenant.user.get_full_name(),
            "phone_number": txn.phone_number,
            "amount": txn.amount,
            "pending_since": txn.created_at,
            "hours_pending": round((timezone.now() - txn.created_at).total_seconds() / 3600, 1),
        }
        for txn in transactions
    ]


def get_integrity_mismatches(user):
    """
    Audit net, not a normal-operation check — these should never
    appear given the clean() guards on PaymentAllocation, but this
    catches drift from anything that bypassed the service layer
    (direct DB edits, Django admin, a future bug). An empty list here
    is the expected, healthy state.
    """
    payments = get_payments_for_user(user)

    mismatches = []
    for payment in payments:
        total_allocated = payment.allocations.aggregate(total=Sum("amount_allocated"))["total"] or Decimal("0")
        if total_allocated > payment.amount:
            mismatches.append({
                "type": "OVER_ALLOCATED_PAYMENT",
                "payment_id": str(payment.id),
                "payment_reference": payment.payment_reference,
                "amount": payment.amount,
                "total_allocated": total_allocated,
                "difference": total_allocated - payment.amount,
            })

        for allocation in payment.allocations.select_related("invoice"):
            invoice = allocation.invoice
            invoice_total_allocated = invoice.payment_allocations.aggregate(
                total=Sum("amount_allocated")
            )["total"] or Decimal("0")
            if invoice.amount_paid != invoice_total_allocated:
                mismatches.append({
                    "type": "INVOICE_AMOUNT_PAID_MISMATCH",
                    "invoice_id": str(invoice.id),
                    "invoice_number": invoice.invoice_number,
                    "recorded_amount_paid": invoice.amount_paid,
                    "actual_allocated_total": invoice_total_allocated,
                })

    # de-duplicate invoice mismatches (same invoice can appear once per allocation)
    seen_invoice_ids = set()
    deduped = []
    for m in mismatches:
        key = m.get("invoice_id") or m.get("payment_id")
        if key in seen_invoice_ids:
            continue
        seen_invoice_ids.add(key)
        deduped.append(m)

    return deduped


def get_reconciliation_dashboard(user):
    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD):
        raise PermissionDenied("Only Admin or Landlord can view reconciliation data.")

    return {
        "unallocated_payments": get_unallocated_payments(user),
        "stale_pending_mpesa": get_stale_pending_mpesa_transactions(user),
        "integrity_mismatches": get_integrity_mismatches(user),
    }


def reconcile_payment(*, payment, user):
    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD):
        raise PermissionDenied("Only Admin or Landlord can reconcile payments.")

    assert_landlord_manages_tenant(tenant=payment.tenant, user=user)

    if payment.status != Payment.Status.CONFIRMED:
        raise ValidationError({"payment": "Only a CONFIRMED payment can be reconciled."})

    if payment.is_reconciled:
        raise ValidationError({"payment": "This payment has already been reconciled."})

    payment.is_reconciled = True
    payment.reconciled_at = timezone.now()
    payment.reconciled_by = user
    payment.save(update_fields=["is_reconciled", "reconciled_at", "reconciled_by", "updated_at"])

    return payment