from decimal import Decimal
from rest_framework import serializers


class ApplyLateFeeSerializer(serializers.Serializer):
    fee_type = serializers.ChoiceField(choices=["FIXED", "PERCENTAGE"])
    value = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0"))


class ApplyLateFeesBatchSerializer(serializers.Serializer):
    billing_period = serializers.UUIDField()
    fee_type = serializers.ChoiceField(choices=["FIXED", "PERCENTAGE"])
    value = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0"))