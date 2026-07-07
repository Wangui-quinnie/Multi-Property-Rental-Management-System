from django.db import models

from apps.accounts.models import User
from apps.core.models import TimeStampedUUIDModel


class Tenant(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        BLACKLISTED = "BLACKLISTED", "Blacklisted"

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="tenant_profile"
    )
    national_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["user__first_name", "user__last_name"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["national_id"]),
        ]

    def __str__(self):
        full_name = self.user.get_full_name()
        return full_name or self.user.email