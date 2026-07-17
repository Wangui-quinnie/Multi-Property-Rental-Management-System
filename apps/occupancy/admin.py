from django.contrib import admin

from .models import Occupancy


@admin.register(Occupancy)
class OccupancyAdmin(admin.ModelAdmin):
    list_display = ("unit", "lease", "status", "move_in_date", "move_out_date")
    search_fields = ("unit__unit_number", "lease__tenant__user__email")