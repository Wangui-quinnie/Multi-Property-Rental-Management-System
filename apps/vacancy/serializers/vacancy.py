from rest_framework import serializers

from ..models import VacancyPeriod


class VacancyPeriodSerializer(serializers.ModelSerializer):
    unit_number = serializers.CharField(source="unit.unit_number", read_only=True)
    property_name = serializers.CharField(source="unit.property.name", read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    days_vacant = serializers.IntegerField(read_only=True)

    class Meta:
        model = VacancyPeriod
        fields = (
            "id", "unit", "unit_number", "property_name",
            "vacated_at", "occupied_at", "is_open", "days_vacant",
            "created_at", "updated_at",
        )
        read_only_fields = fields