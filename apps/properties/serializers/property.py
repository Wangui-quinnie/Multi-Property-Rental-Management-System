# apps/properties/serializers/property.py
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.accounts.models import User

from ..models import Property


class PropertySerializer(serializers.ModelSerializer):
    landlord_name = serializers.CharField(source="landlord.get_full_name", read_only=True)

    total_units = serializers.IntegerField(read_only=True)
    occupied_units = serializers.IntegerField(read_only=True)
    vacant_units = serializers.IntegerField(read_only=True)
    maintenance_units = serializers.IntegerField(read_only=True)
    potential_monthly_rent = serializers.SerializerMethodField()
    occupancy_rate = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            "id", "landlord", "landlord_name", "name", "code", "location",
            "address", "status", "is_archived", "archived_at",
            "total_units", "occupied_units", "vacant_units", "maintenance_units",
            "potential_monthly_rent", "occupancy_rate", "created_at", "updated_at",
        )
        read_only_fields = ("id", "is_archived", "archived_at", "created_at", "updated_at")

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_potential_monthly_rent(self, obj):
        return obj.potential_monthly_rent or 0

    @extend_schema_field(serializers.FloatField())
    def get_occupancy_rate(self, obj):
        total = obj.total_units or 0
        occupied = obj.occupied_units or 0
        return round((occupied / total) * 100, 2) if total else 0.0


class PropertyCreateSerializer(serializers.ModelSerializer):
    landlord = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.LANDLORD),
        required=False,
    )

    class Meta:
        model = Property
        fields = ("landlord", "name", "code", "location", "address", "status")

    def validate_landlord(self, landlord):
        if landlord.role != User.Role.LANDLORD:
            raise serializers.ValidationError("Selected user must have the LANDLORD role.")
        return landlord


class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ("name", "location", "address", "status")