from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import User
from apps.core.models import TimeStampedUUIDModel


class Property(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    landlord = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="properties"
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["landlord"]),
            models.Index(fields=["location"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name


class Unit(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        VACANT = "VACANT", "Vacant"
        OCCUPIED = "OCCUPIED", "Occupied"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        INACTIVE = "INACTIVE", "Inactive"

    property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name="units"
    )
    unit_number = models.CharField(max_length=50)
    unit_type = models.CharField(max_length=80, blank=True)
    floor_number = models.IntegerField(null=True, blank=True)
    rent_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.VACANT,
        db_index=True
    )

    class Meta:
        ordering = ["property__name", "unit_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["property", "unit_number"],
                name="unique_unit_per_property"
            )
        ]
        indexes = [
            models.Index(fields=["property", "status"]),
            models.Index(fields=["unit_number"]),
        ]

    def __str__(self):
        return f"{self.property.name} - {self.unit_number}"