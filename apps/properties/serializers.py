from rest_framework import serializers

from apps.accounts.models import User

from .models import Property, Unit

#read responses
class PropertySerializer(serializers.ModelSerializer):
    landlord_name = serializers.CharField(
        source="landlord.get_full_name",
        read_only=True
    )

    total_units = serializers.SerializerMethodField()
    occupied_units = serializers.SerializerMethodField()
    vacant_units = serializers.SerializerMethodField()

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

    def get_total_units(self, obj):
        return obj.units.count()

    def get_occupied_units(self, obj):
        return obj.units.filter(
            status=Unit.Status.OCCUPIED
    ).count()


    def get_vacant_units(self, obj):
        return obj.units.filter(
            status=Unit.Status.VACANT
        ).count()
    


#create
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

#update 
class PropertyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            "name",
            "location",
            "address",
            "status",
        )