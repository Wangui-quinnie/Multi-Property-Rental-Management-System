from rest_framework import serializers

from apps.properties.models import Unit


class UnitSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(
        source="property.name",
        read_only=True,
    )

    landlord_name = serializers.CharField(
        source="property.landlord.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Unit
        fields = (
            "id",
            "property",
            "property_name",
            "landlord_name",
            "unit_number",
            "unit_type",
            "floor_number",
            "rent_amount",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class UnitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = (
            "property",
            "unit_number",
            "unit_type",
            "floor_number",
            "rent_amount",
            "status",
        )


class UnitUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = (
            "unit_type",
            "floor_number",
            "rent_amount",
            "status",
        )