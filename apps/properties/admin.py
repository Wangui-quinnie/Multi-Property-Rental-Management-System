from django.contrib import admin
from .models import Property, Unit


class UnitInline(admin.TabularInline):
    model = Unit
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "landlord",
        "location",
        "status",
        "created_at",
    ]
    list_filter = ["status", "location"]
    search_fields = ["name", "code", "location", "landlord__email"]
    inlines = [UnitInline]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = [
        "unit_number",
        "property",
        "unit_type",
        "rent_amount",
        "status",
    ]
    list_filter = ["status", "property"]
    search_fields = ["unit_number", "property__name"]