from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from decimal import Decimal
from django.db.models import Sum

from apps.billing.models import Invoice
from apps.core.models import TimeStampedUUIDModel
from apps.tenants.models import Tenant


class Payment(TimeStampedUUIDModel):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        MPESA = "MPESA", "Mpesa"
        CARD = "CARD", "Card"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        FAILED = "FAILED", "Failed"
        REVERSED = "REVERSED", "Reversed"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        related_name="payments"
    )
    payment_reference = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(
        max_length=30,
        choices=Method.choices,
        db_index=True
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    payment_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
        db_index=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["tenant", "payment_date"]),
            models.Index(fields=["payment_method"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.payment_reference} - {self.amount}"


class PaymentAllocation(TimeStampedUUIDModel):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="allocations"
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="payment_allocations"
    )
    amount_allocated = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    class Meta:
        verbose_name = "Payment Allocation"
        verbose_name_plural = "Payment Allocations"
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "invoice"],
                name="unique_payment_invoice_allocation"
            )
        ]
        indexes = [
            models.Index(fields=["payment"]),
            models.Index(fields=["invoice"]),
        ]

    def clean(self):
        
        if self.invoice.lease.tenant_id != self.payment.tenant_id:
            raise ValidationError("Payment tenant must match invoice tenant.")

        if self.amount_allocated > self.invoice.balance:
            raise ValidationError("Allocation cannot exceed invoice balance.")

        already_allocated = self.payment.allocations.exclude(pk=self.pk).aggregate(
            total=Sum("amount_allocated")
        )["total"] or Decimal("0")

        if already_allocated + self.amount_allocated > self.payment.amount:
            raise ValidationError("Total allocations cannot exceed the payment amount.")
    def save(self, *args, **kwargs):
        self.full_clean()

        with transaction.atomic():
            super().save(*args, **kwargs)
            self.update_invoice_balance()

    def update_invoice_balance(self):
        invoice = self.invoice

        total_allocated = sum(
            allocation.amount_allocated
            for allocation in invoice.payment_allocations.all()
        )

        invoice.amount_paid = total_allocated
        invoice.save(update_fields=["amount_paid", "updated_at"])
        invoice.refresh_totals()

    def __str__(self):
        return f"{self.payment} -> {self.invoice}"

class MpesaTransaction(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        related_name="mpesa_transactions"
    )
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1"))]
    )
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    result_code = models.CharField(max_length=10, blank=True)
    result_description = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mpesa_transaction"
    )

    class Meta:
        verbose_name = "M-Pesa Transaction"
        verbose_name_plural = "M-Pesa Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["checkout_request_id"]),
        ]

    def __str__(self):
        return f"{self.checkout_request_id} - {self.status}"