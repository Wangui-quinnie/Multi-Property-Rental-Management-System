from ..models import Payment


def get_receipt_data(*, payment):
    """
    Composes a structured receipt from an existing confirmed Payment.
    Receipts are never stored — always assembled fresh from the
    Payment and its allocations, so they can never go stale relative
    to the underlying data.
    """
    if payment.status != Payment.Status.CONFIRMED:
        from rest_framework.exceptions import ValidationError
        raise ValidationError(
            {"payment": "Only a CONFIRMED payment has a valid receipt."}
        )

    allocations = payment.allocations.select_related(
        "invoice__lease__unit__property", "invoice__lease__unit"
    )

    allocation_lines = [
        {
            "invoice_number": alloc.invoice.invoice_number,
            "unit_number": alloc.invoice.lease.unit.unit_number,
            "property_name": alloc.invoice.lease.unit.property.name,
            "amount_allocated": alloc.amount_allocated,
        }
        for alloc in allocations
    ]

    total_allocated = sum(a.amount_allocated for a in allocations)

    return {
        "receipt_number": f"RCT-{str(payment.id)[:8].upper()}",
        "payment_reference": payment.payment_reference,
        "payment_method": payment.payment_method,
        "payment_date": payment.payment_date,
        "amount_paid": payment.amount,
        "tenant_name": payment.tenant.user.get_full_name(),
        "tenant_email": payment.tenant.user.email,
        "allocations": allocation_lines,
        "total_allocated": total_allocated,
        "unallocated_amount": payment.amount - total_allocated,
        "notes": payment.notes,
    }