from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedUUIDModel
from apps.properties.models import Unit
from apps.tenants.models import Tenant


class Lease(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ENDED = "ENDED", "Ended"
        CANCELLED = "CANCELLED", "Cancelled"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        related_name="leases"
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="leases"
    )
    lease_start_date = models.DateField()
    lease_end_date = models.DateField(blank=True, null=True)
    rent_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    billing_day = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    class Meta:
        verbose_name = "Lease"
        verbose_name_plural = "Leases"
        ordering = ["-lease_start_date"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["unit", "status"]),
            models.Index(fields=["lease_start_date", "lease_end_date"]),
        ]

    def clean(self):
        if self.lease_end_date and self.lease_end_date < self.lease_start_date:
            raise ValidationError("Lease end date cannot be before lease start date.")

        if not 1 <= self.billing_day <= 31:
            raise ValidationError("Billing day must be between 1 and 31.")

        active_lease_exists = Lease.objects.filter(
            unit=self.unit,
            status=Lease.Status.ACTIVE
        ).exclude(pk=self.pk).exists()

        if self.status == Lease.Status.ACTIVE and active_lease_exists:
            raise ValidationError("This unit already has an active lease.")

    def __str__(self):
        return f"{self.tenant} - {self.unit}"