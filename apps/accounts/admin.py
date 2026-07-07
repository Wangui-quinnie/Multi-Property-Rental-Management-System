from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        "email",
        "username",
        "role",
        "phone_number",
        "is_staff",
        "is_active",
    ]

    list_filter = [
        "role",
        "is_staff",
        "is_active",
        "is_email_verified",
    ]

    search_fields = [
        "email",
        "username",
        "first_name",
        "last_name",
        "phone_number",
    ]

    ordering = ["email"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Rental System Details",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "is_email_verified",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Rental System Details",
            {
                "fields": (
                    "email",
                    "role",
                    "phone_number",
                )
            },
        ),
    )