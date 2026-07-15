# apps/properties/serializers/unit.py
from rest_framework import serializers

from ..models import Unit


class UnitSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source="property.name", read_only=True)
    landlord_name = serializers.CharField(source="property.landlord.get_full_name", read_only=True)

    class Meta:
        model = Unit
        fields = (
            "id", "property", "property_name", "landlord_name",
            "unit_number", "unit_type", "floor_number", "rent_amount", "status",
            "is_archived", "archived_at", "created_at", "updated_at",
        )
        read_only_fields = ("id", "is_archived", "archived_at", "created_at", "updated_at")


class UnitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("property", "unit_number", "unit_type", "floor_number", "rent_amount", "status")
        validators = []  # disable auto unique_together validator; validate() below handles it with a clearer error

    def validate(self, attrs):
        property_obj = attrs.get("property")
        unit_number = attrs.get("unit_number")

        if Unit.objects.filter(property=property_obj, unit_number=unit_number).exists():
            raise serializers.ValidationError(
                {"unit_number": "A unit with this number already exists in this property."}
            )

        return attrs


class UnitUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("unit_type", "floor_number", "rent_amount", "status")