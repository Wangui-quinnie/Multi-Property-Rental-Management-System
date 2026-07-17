from rest_framework import serializers

from ..models import Occupancy


class OccupancySerializer(serializers.ModelSerializer):
    """Read serializer — list/retrieve."""
    tenant_name = serializers.CharField(source="lease.tenant.user.get_full_name", read_only=True)
    unit_number = serializers.CharField(source="unit.unit_number", read_only=True)
    property_name = serializers.CharField(source="unit.property.name", read_only=True)

    class Meta:
        model = Occupancy
        fields = (
            "id", "lease", "unit", "tenant_name", "unit_number", "property_name",
            "move_in_date", "move_out_date", "status", "created_at", "updated_at",
        )
        read_only_fields = fields


class OccupancyActivateSerializer(serializers.Serializer):
    """
    Input serializer for the activation action. Only `lease` is
    required from the client — move_in_date defaults to today if
    omitted, since that's the common case (activating occupancy on
    the day the tenant actually moves in).
    """
    lease = serializers.UUIDField()
    move_in_date = serializers.DateField(required=False)