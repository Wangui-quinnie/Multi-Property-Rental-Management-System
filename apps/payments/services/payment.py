from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.leases.models import Lease
from apps.billing.models import Invoice


from ..models import Payment, PaymentAllocation


def assert_landlord_manages_tenant(*, tenant, user):
    if user.role == user.Role.LANDLORD:
        has_lease_with_landlord = Lease.objects.filter(
            tenant=tenant, unit__property__landlord=user
        ).exists()
        if not has_lease_with_landlord:
            raise PermissionDenied(
                "You can only record payments for tenants who have a lease on one of your units."
            )


def create_payment(*, serializer, user):
    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD):
        raise PermissionDenied("Only Admin or Landlord can record payments.")

    tenant = serializer.validated_data["tenant"]
    assert_landlord_manages_tenant(tenant=tenant, user=user)
    serializer.save()


def _run_clean(allocation):
    try:
        allocation.clean()
    except DjangoValidationError as exc:
        if hasattr(exc, "message_dict"):
            raise ValidationError(exc.message_dict)
        raise ValidationError({"non_field_errors": exc.messages})


def allocate_payment_to_invoice(*, payment, invoice, amount, user):
    assert_landlord_manages_tenant(tenant=payment.tenant, user=user)

    allocation = PaymentAllocation(payment=payment, invoice=invoice, amount_allocated=amount)
    _run_clean(allocation)
    allocation.save()
    return allocation


def _allocate_payment_to_oldest_invoices_core(*, payment):
    """
    The actual allocation logic, with no permission check. Called by:
      - allocate_payment_to_oldest_invoices() below, after it verifies
        the requesting human is allowed to act on this payment
      - process_stk_callback() in mpesa.py, which has no human user at
        all — it's triggered by a verified Safaricom callback, not a
        request a permission check makes sense against
    """
    already_allocated = sum(a.amount_allocated for a in payment.allocations.all())
    remaining_amount = payment.amount - already_allocated

    unpaid_invoices = Invoice.objects.filter(
        lease__tenant=payment.tenant,
        status__in=[Invoice.Status.UNPAID, Invoice.Status.PARTIALLY_PAID, Invoice.Status.OVERDUE],
    ).order_by("due_date")

    allocations = []
    for invoice in unpaid_invoices:
        if remaining_amount <= 0:
            break

        amount_to_allocate = min(remaining_amount, invoice.balance)
        if amount_to_allocate <= 0:
            continue

        allocation = PaymentAllocation(payment=payment, invoice=invoice, amount_allocated=amount_to_allocate)
        _run_clean(allocation)
        allocation.save()

        allocations.append(allocation)
        remaining_amount -= amount_to_allocate

    return allocations


def allocate_payment_to_oldest_invoices(*, payment, user):
    """
    Human/API entry point — verifies the requesting user is allowed
    to act on this payment before delegating to the core logic.
    """
    assert_landlord_manages_tenant(tenant=payment.tenant, user=user)
    return _allocate_payment_to_oldest_invoices_core(payment=payment)

def remove_allocation(*, allocation, user):
    """
    Removes a single misallocated PaymentAllocation. The invoice's
    amount_paid/balance/status are automatically recomputed via
    PaymentAllocation's post-save propagation — but since delete()
    doesn't trigger save(), we must call update_invoice_balance()
    explicitly here after removal.
    """
    assert_landlord_manages_tenant(tenant=allocation.payment.tenant, user=user)

    invoice = allocation.invoice
    allocation.delete()
    invoice.refresh_from_db()

    total_allocated = sum(a.amount_allocated for a in invoice.payment_allocations.all())
    invoice.amount_paid = total_allocated
    invoice.save(update_fields=["amount_paid", "updated_at"])
    invoice.refresh_totals()