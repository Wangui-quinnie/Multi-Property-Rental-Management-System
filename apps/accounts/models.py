import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        LANDLORD = "LANDLORD", "Landlord"
        TENANT = "TENANT", "Tenant"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TENANT
    )
    phone_number = models.CharField(max_length=30, blank=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        full_name = self.get_full_name()
        display_name = full_name if full_name else self.email
        return f"{display_name} ({self.role})"

    @property
    def is_admin_or_landlord(self):
        return self.role in [self.Role.ADMIN, self.Role.LANDLORD]

    @property
    def is_tenant_user(self):
        return self.role == self.Role.TENANT