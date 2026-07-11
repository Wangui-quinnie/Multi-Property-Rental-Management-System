from rest_framework import serializers

from apps.accounts.models import User

from .models import Property, Unit


# ---- Property: read (GET) ----
class PropertySerializer(serializers.ModelSerializer):
    landlord_name = serializers.CharField(
        source="landlord.get_full_name",
        read_only=True,
    )

    # These arrive pre-computed from get_queryset()'s .annotate() call
    # in views.py — no method needed, they're just plain attributes
    # Django attaches to each Property object at query time.
    total_units = serializers.IntegerField(read_only=True)
    occupied_units = serializers.IntegerField(read_only=True)
    vacant_units = serializers.IntegerField(read_only=True)

    class Meta:
        model = Property
        fields = (
            "id",
            "landlord",
            "landlord_name",
            "name",
            "code",
            "location",
            "address",
            "status",
            "total_units",
            "occupied_units",
            "vacant_units",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


# ---- Property: create ----
class PropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            "landlord",
            "name",
            "code",
            "location",
            "address",
            "status",
        )

    def validate_landlord(self, landlord):
        if landlord.role != User.Role.LANDLORD:
            raise serializers.ValidationError(
                "Selected user must have the LANDLORD role."
            )
        return landlord


# ---- Property: update ----
class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            "name",
            "location",
            "address",
            "status",
        )


# ---- Unit: read (GET) ----
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


# ---- Unit: create ----
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


# ---- Unit: update ----
class UnitUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = (
            "unit_type",
            "floor_number",
            "rent_amount",
            "status",
        )