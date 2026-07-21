from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import WaterMeterReading


def _clean_reading(*, instance, attrs):
    def field(name, default=None):
        if name in attrs:
            return attrs[name]
        if instance is not None:
            return getattr(instance, name)
        return default

    temp = WaterMeterReading(
        pk=instance.pk if instance else None,
        unit=field("unit"),
        billing_period=field("billing_period"),
        previous_reading=field("previous_reading", 0),
        current_reading=field("current_reading"),
        rate_per_unit=field("rate_per_unit"),
        reading_date=field("reading_date"),
    )

    try:
        temp.clean()
    except DjangoValidationError as exc:
        if hasattr(exc, "message_dict"):
            raise serializers.ValidationError(exc.message_dict)
        raise serializers.ValidationError({"non_field_errors": exc.messages})


class WaterMeterReadingSerializer(serializers.ModelSerializer):
    unit_number = serializers.CharField(source="unit.unit_number", read_only=True)
    property_name = serializers.CharField(source="unit.property.name", read_only=True)
    billing_period_name = serializers.CharField(source="billing_period.name", read_only=True)
    is_billed = serializers.SerializerMethodField()

    class Meta:
        model = WaterMeterReading
        fields = (
            "id", "unit", "unit_number", "property_name", "billing_period",
            "billing_period_name", "previous_reading", "current_reading",
            "units_consumed", "rate_per_unit", "amount", "reading_date",
            "invoice_item", "is_billed", "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_is_billed(self, obj):
        return obj.invoice_item_id is not None


class WaterMeterReadingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterMeterReading
        fields = ("unit", "billing_period", "previous_reading", "current_reading", "rate_per_unit", "reading_date")
        validators = []  # disable auto unique_together validator; clean() gives a clearer error below

    def validate(self, attrs):
        _clean_reading(instance=None, attrs=attrs)

        unit = attrs["unit"]
        billing_period = attrs["billing_period"]
        if WaterMeterReading.objects.filter(unit=unit, billing_period=billing_period).exists():
            raise serializers.ValidationError(
                {"billing_period": "A reading already exists for this unit in this billing period."}
            )

        return attrs


class WaterMeterReadingUpdateSerializer(serializers.ModelSerializer):
    """
    Deliberately excludes `unit` and `billing_period` — those define
    which reading this is, not correctable fields.
    """
    class Meta:
        model = WaterMeterReading
        fields = ("previous_reading", "current_reading", "rate_per_unit", "reading_date")

    def validate(self, attrs):
        _clean_reading(instance=self.instance, attrs=attrs)
        return attrs