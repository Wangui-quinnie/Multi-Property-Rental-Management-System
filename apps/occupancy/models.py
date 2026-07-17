from django.db import models

from apps.core.models import TimeStampedUUIDModel
from apps.leases.models import Lease
from apps.properties.models import Unit


class Occupancy(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ENDED = "ENDED", "Ended"

    lease = models.OneToOneField(
        Lease,
        on_delete=models.PROTECT,
        related_name="occupancy",
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="occupancies",
    )
    move_in_date = models.DateField()
    move_out_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    class Meta:
        verbose_name = "Occupancy"
        verbose_name_plural = "Occupancies"
        ordering = ["-move_in_date"]
        indexes = [
            models.Index(fields=["unit", "status"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.unit} — {self.lease.tenant} ({self.status})"