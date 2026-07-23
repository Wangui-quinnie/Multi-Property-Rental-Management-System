from rest_framework import serializers


class UnallocatedPaymentSerializer(serializers.Serializer):
    payment_id = serializers.UUIDField()
    payment_reference = serializers.CharField()
    tenant_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_allocated = serializers.DecimalField(max_digits=12, decimal_places=2)
    unallocated_amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class StalePendingMpesaSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    checkout_request_id = serializers.CharField()
    tenant_name = serializers.CharField()
    phone_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_since = serializers.DateTimeField()
    hours_pending = serializers.FloatField()


class IntegrityMismatchSerializer(serializers.Serializer):
    type = serializers.CharField()
    payment_id = serializers.UUIDField(required=False)
    payment_reference = serializers.CharField(required=False)
    invoice_id = serializers.UUIDField(required=False)
    invoice_number = serializers.CharField(required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_allocated = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    difference = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    recorded_amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    actual_allocated_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


class ReconciliationDashboardSerializer(serializers.Serializer):
    unallocated_payments = UnallocatedPaymentSerializer(many=True)
    stale_pending_mpesa = StalePendingMpesaSerializer(many=True)
    integrity_mismatches = IntegrityMismatchSerializer(many=True)