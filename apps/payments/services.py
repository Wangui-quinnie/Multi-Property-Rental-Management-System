from django.db import transaction

from apps.billing.models import Invoice
from apps.payments.models import Payment, PaymentAllocation


@transaction.atomic
def allocate_payment_to_invoice(payment, invoice, amount):
    allocation = PaymentAllocation.objects.create(
        payment=payment,
        invoice=invoice,
        amount_allocated=amount,
    )
    return allocation


@transaction.atomic
def allocate_payment_to_oldest_invoices(payment):
    remaining_amount = payment.amount

    unpaid_invoices = Invoice.objects.filter(
        lease__tenant=payment.tenant,
        status__in=[
            Invoice.Status.UNPAID,
            Invoice.Status.PARTIALLY_PAID,
            Invoice.Status.OVERDUE,
        ]
    ).order_by("due_date")

    allocations = []

    for invoice in unpaid_invoices:
        if remaining_amount <= 0:
            break

        amount_to_allocate = min(remaining_amount, invoice.balance)

        allocation = PaymentAllocation.objects.create(
            payment=payment,
            invoice=invoice,
            amount_allocated=amount_to_allocate,
        )

        allocations.append(allocation)
        remaining_amount -= amount_to_allocate

    return allocations