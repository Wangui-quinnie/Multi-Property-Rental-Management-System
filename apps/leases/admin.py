from django.contrib import admin
from .models import Lease


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = [
        "tenant",
        "unit",
        "lease_start_date",
        "lease_end_date",
        "rent_amount",
        "status",
    ]
    list_filter = ["status", "lease_start_date"]
    search_fields = [
        "tenant__user__email",
        "tenant__user__first_name",
        "tenant__user__last_name",
        "unit__unit_number",
        "unit__property__name",
    ]