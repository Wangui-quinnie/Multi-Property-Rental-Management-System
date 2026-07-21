from rest_framework import serializers


class ReceiptAllocationLineSerializer(serializers.Serializer):
    invoice_number = serializers.CharField()
    unit_number = serializers.CharField()
    property_name = serializers.CharField()
    amount_allocated = serializers.DecimalField(max_digits=12, decimal_places=2)


class ReceiptSerializer(serializers.Serializer):
    receipt_number = serializers.CharField()
    payment_reference = serializers.CharField()
    payment_method = serializers.CharField()
    payment_date = serializers.DateTimeField()
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    tenant_name = serializers.CharField()
    tenant_email = serializers.EmailField()
    allocations = ReceiptAllocationLineSerializer(many=True)
    total_allocated = serializers.DecimalField(max_digits=12, decimal_places=2)
    unallocated_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(allow_blank=True)