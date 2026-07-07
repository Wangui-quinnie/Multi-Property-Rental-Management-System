from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedUUIDModel
from apps.leases.models import Lease
from apps.properties.models import Unit


class BillingPeriod(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"

    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True
    )

    class Meta:
        verbose_name = "Billing Period"
        verbose_name_plural = "Billing Periods"
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["start_date", "end_date"],
                name="unique_billing_period_dates"
            )
        ]

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
        if self.due_date < self.start_date:
            raise ValidationError("Due date cannot be before start date.")

    def __str__(self):
        return self.name


class Invoice(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        UNPAID = "UNPAID", "Unpaid"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Paid"
        OVERDUE = "OVERDUE", "Overdue"
        CANCELLED = "CANCELLED", "Cancelled"

    lease = models.ForeignKey(
        Lease,
        on_delete=models.PROTECT,
        related_name="invoices"
    )
    billing_period = models.ForeignKey(
        BillingPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices"
    )
    invoice_number = models.CharField(max_length=80, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.UNPAID,
        db_index=True
    )

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-invoice_date"]
        indexes = [
            models.Index(fields=["lease", "status"]),
            models.Index(fields=["billing_period"]),
            models.Index(fields=["status", "due_date"]),
        ]

    def clean(self):
        if self.amount_paid > self.total_amount:
            raise ValidationError("Amount paid cannot be greater than total amount.")

    def refresh_totals(self):
        subtotal = sum(item.amount for item in self.items.all())
        self.subtotal = subtotal
        self.total_amount = subtotal + self.tax_amount
        self.balance = self.total_amount - self.amount_paid

        if self.balance == 0:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIALLY_PAID
        else:
            self.status = self.Status.UNPAID

        self.save(update_fields=[
            "subtotal",
            "total_amount",
            "balance",
            "status",
            "updated_at",
        ])

    def __str__(self):
        return self.invoice_number


class InvoiceItem(TimeStampedUUIDModel):
    class ItemType(models.TextChoices):
        RENT = "RENT", "Rent"
        WATER = "WATER", "Water"
        ELECTRICITY = "ELECTRICITY", "Electricity"
        GARBAGE = "GARBAGE", "Garbage"
        SERVICE_CHARGE = "SERVICE_CHARGE", "Service Charge"
        PENALTY = "PENALTY", "Penalty"
        DEPOSIT = "DEPOSIT", "Deposit"
        OTHER = "OTHER", "Other"

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )
    item_type = models.CharField(
        max_length=30,
        choices=ItemType.choices,
        db_index=True
    )
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0)]
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = "Invoice Item"
        verbose_name_plural = "Invoice Items"
        indexes = [
            models.Index(fields=["invoice", "item_type"]),
        ]

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.invoice.refresh_totals()

    def __str__(self):
        return f"{self.item_type} - {self.amount}"


class WaterMeterReading(TimeStampedUUIDModel):
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="water_readings"
    )
    billing_period = models.ForeignKey(
        BillingPeriod,
        on_delete=models.PROTECT,
        related_name="water_readings"
    )
    previous_reading = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    current_reading = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    units_consumed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    rate_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    reading_date = models.DateField()
    invoice_item = models.OneToOneField(
        InvoiceItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="water_reading"
    )

    class Meta:
        verbose_name = "Water Meter Reading"
        verbose_name_plural = "Water Meter Readings"
        ordering = ["-reading_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["unit", "billing_period"],
                name="unique_water_reading_per_unit_period"
            )
        ]
        indexes = [
            models.Index(fields=["unit", "billing_period"]),
            models.Index(fields=["reading_date"]),
        ]

    def clean(self):
        if self.current_reading < self.previous_reading:
            raise ValidationError("Current reading cannot be less than previous reading.")

    def save(self, *args, **kwargs):
        self.units_consumed = self.current_reading - self.previous_reading
        self.amount = self.units_consumed * self.rate_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unit} - {self.billing_period}"