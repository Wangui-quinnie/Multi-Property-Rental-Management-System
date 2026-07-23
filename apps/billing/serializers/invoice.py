from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field
from ..models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ("id", "item_type", "description", "quantity", "unit_price", "amount", "created_at")
        read_only_fields = fields


class InvoiceSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="lease.tenant.user.get_full_name", read_only=True)
    unit_number = serializers.CharField(source="lease.unit.unit_number", read_only=True)
    property_name = serializers.CharField(source="lease.unit.property.name", read_only=True)
    billing_period_name = serializers.CharField(source="billing_period.name", read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = (
            "id", "lease", "tenant_name", "unit_number", "property_name",
            "billing_period", "billing_period_name", "invoice_number",
            "invoice_date", "due_date", "subtotal", "tax_amount",
            "total_amount", "amount_paid", "balance", "status", "is_overdue",
            "items", "created_at", "updated_at",
        )
        read_only_fields = fields

    
    @extend_schema_field(serializers.BooleanField())
    def get_is_overdue(self, obj):
        return obj.is_currently_overdue()


class GenerateRentInvoicesSerializer(serializers.Serializer):
    billing_period = serializers.UUIDField()