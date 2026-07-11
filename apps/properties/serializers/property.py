from rest_framework import serializers

from apps.accounts.models import User
from apps.properties.models import Property


class PropertySerializer(serializers.ModelSerializer):
    landlord_name = serializers.CharField(
        source="landlord.get_full_name",
        read_only=True,
    )

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


class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            "name",
            "location",
            "address",
            "status",
        )