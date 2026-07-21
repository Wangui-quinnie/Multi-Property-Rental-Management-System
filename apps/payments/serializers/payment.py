from decimal import Decimal

from rest_framework import serializers

from apps.tenants.models import Tenant

from ..models import Payment, PaymentAllocation


class PaymentAllocationSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)

    class Meta:
        model = PaymentAllocation
        fields = ("id", "payment", "invoice", "invoice_number", "amount_allocated", "created_at")
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.user.get_full_name", read_only=True)
    allocations = PaymentAllocationSerializer(many=True, read_only=True)
    total_allocated = serializers.SerializerMethodField()
    unallocated_amount = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id", "tenant", "tenant_name", "payment_reference", "payment_method",
            "amount", "payment_date", "status", "notes",
            "allocations", "total_allocated", "unallocated_amount",
            "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_total_allocated(self, obj):
        return sum(a.amount_allocated for a in obj.allocations.all())

    def get_unallocated_amount(self, obj):
        return obj.amount - self.get_total_allocated(obj)


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("tenant", "payment_reference", "payment_method", "amount", "payment_date", "status", "notes")


class AllocateToInvoiceSerializer(serializers.Serializer):
    invoice = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))