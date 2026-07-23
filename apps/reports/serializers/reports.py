from rest_framework import serializers


class RentReportSerializer(serializers.Serializer):
    rent_billed = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_billed = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_collected = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_outstanding = serializers.DecimalField(max_digits=14, decimal_places=2)
    invoice_count = serializers.IntegerField()


class WaterReportSerializer(serializers.Serializer):
    total_units_consumed = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_water_billed = serializers.DecimalField(max_digits=14, decimal_places=2)
    reading_count = serializers.IntegerField()


class CashFlowEntrySerializer(serializers.Serializer):
    month = serializers.CharField()
    total_collected = serializers.DecimalField(max_digits=14, decimal_places=2)