from django.contrib import admin
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "national_id",
        "status",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "national_id",
    ]