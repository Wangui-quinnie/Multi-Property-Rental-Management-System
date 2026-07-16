from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import Lease


def _build_temp_lease_and_clean(*, instance, attrs):
    """
    Reuses Lease.clean() as the single source of truth for business
    rules (one active lease per unit, valid billing day, end date not
    before start date) instead of duplicating that logic here.

    Falls back to the existing instance's values for any field not
    present in attrs, so this works correctly for both full creates
    and partial (PATCH) updates.
    """
    def field(name, default=None):
        if name in attrs:
            return attrs[name]
        if instance is not None:
            return getattr(instance, name)
        return default

    temp = Lease(
        pk=instance.pk if instance else None,
        unit=field("unit"),
        tenant=field("tenant"),
        lease_start_date=field("lease_start_date"),
        lease_end_date=field("lease_end_date"),
        rent_amount=field("rent_amount"),
        deposit_amount=field("deposit_amount", 0),
        billing_day=field("billing_day", 1),
        status=field("status", Lease.Status.ACTIVE),
    )

    try:
        temp.clean()
    except DjangoValidationError as exc:
        if hasattr(exc, "message_dict"):
            raise serializers.ValidationError(exc.message_dict)
        raise serializers.ValidationError({"non_field_errors": exc.messages})


class LeaseSerializer(serializers.ModelSerializer):
    """Read serializer — list/retrieve."""
    tenant_name = serializers.CharField(source="tenant.user.get_full_name", read_only=True)
    unit_number = serializers.CharField(source="unit.unit_number", read_only=True)
    property_name = serializers.CharField(source="unit.property.name", read_only=True)

    class Meta:
        model = Lease
        fields = (
            "id", "tenant", "tenant_name", "unit", "unit_number", "property_name",
            "lease_start_date", "lease_end_date", "rent_amount", "deposit_amount",
            "billing_day", "status", "created_at", "updated_at",
        )
        read_only_fields = fields


class LeaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lease
        fields = (
            "tenant", "unit", "lease_start_date", "lease_end_date",
            "rent_amount", "deposit_amount", "billing_day", "status",
        )

    def validate(self, attrs):
        _build_temp_lease_and_clean(instance=None, attrs=attrs)
        return attrs


class LeaseUpdateSerializer(serializers.ModelSerializer):
    """
    Deliberately excludes `tenant` and `unit` — reassigning a lease to
    a different tenant/unit isn't an "update," it's a new lease. This
    mirrors PropertyUpdateSerializer excluding `landlord` and
    UnitUpdateSerializer excluding `property`.
    """
    class Meta:
        model = Lease
        fields = (
            "lease_start_date", "lease_end_date", "rent_amount",
            "deposit_amount", "billing_day", "status",
        )

    def validate(self, attrs):
        _build_temp_lease_and_clean(instance=self.instance, attrs=attrs)
        return attrs