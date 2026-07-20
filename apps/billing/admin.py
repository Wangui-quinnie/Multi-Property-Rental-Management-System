from django.contrib import admin
from .models import BillingPeriod, Invoice, InvoiceItem, WaterMeterReading


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ["amount"]



@admin.register(BillingPeriod)
class BillingPeriodAdmin(admin.ModelAdmin):
    list_display = ["name", "start_date", "end_date", "due_date", "status"]
    list_filter = ["status"]
    search_fields = ["name"]
    actions = ["generate_rent_invoices"]

    def generate_rent_invoices(self, request, queryset):
        from apps.billing.services import generate_monthly_rent_invoices

        total_created = 0

        for billing_period in queryset:
            invoices = generate_monthly_rent_invoices(billing_period, request.user)
            total_created += len(invoices)

        self.message_user(
        request,
        f"Generated or refreshed {total_created} rent invoice(s)."
      )
    generate_rent_invoices.short_description = "Generate rent invoices for selected billing periods"

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "lease",
        "billing_period",
        "total_amount",
        "amount_paid",
        "balance",
        "status",
        "due_date",
    ]
    list_filter = ["status", "billing_period"]
    search_fields = [
        "invoice_number",
        "lease__tenant__user__email",
        "lease__tenant__user__first_name",
        "lease__tenant__user__last_name",
    ]
    inlines = [InvoiceItemInline]
    readonly_fields = ["subtotal", "total_amount", "amount_paid", "balance"]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ["invoice", "item_type", "description", "quantity", "unit_price", "amount"]
    list_filter = ["item_type"]
    search_fields = ["invoice__invoice_number", "description"]
    readonly_fields = ["amount"]


@admin.register(WaterMeterReading)
class WaterMeterReadingAdmin(admin.ModelAdmin):
    list_display = [
        "unit",
        "billing_period",
        "previous_reading",
        "current_reading",
        "units_consumed",
        "rate_per_unit",
        "amount",
        "reading_date",
    ]
    list_filter = ["billing_period", "reading_date"]
    search_fields = ["unit__unit_number", "unit__property__name"]
    readonly_fields = ["units_consumed", "amount"]
    actions = ["create_water_invoice_items"]

    def create_water_invoice_items(self, request, queryset):
        from apps.billing.services import add_water_charge_to_invoice

        total_created = 0

        for reading in queryset:
            add_water_charge_to_invoice(reading)
            total_created += 1

        self.message_user(
            request,
            f"Created {total_created} water invoice item(s)."
        )

    create_water_invoice_items.short_description = "Create water invoice items for selected readings"