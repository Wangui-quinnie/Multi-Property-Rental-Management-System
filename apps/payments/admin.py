from django.contrib import admin
from .models import Payment, PaymentAllocation


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 1


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "payment_reference",
        "tenant",
        "payment_method",
        "amount",
        "payment_date",
        "status",
    ]
    list_filter = ["payment_method", "status", "payment_date"]
    search_fields = [
        "payment_reference",
        "tenant__user__email",
        "tenant__user__first_name",
        "tenant__user__last_name",
    ]
    inlines = [PaymentAllocationInline]


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = [
        "payment",
        "invoice",
        "amount_allocated",
        "created_at",
    ]
    search_fields = [
        "payment__payment_reference",
        "invoice__invoice_number",
    ]