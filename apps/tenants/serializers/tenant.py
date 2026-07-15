from rest_framework import serializers

from apps.accounts.models import User

from ..models import Tenant
from ..services import create_tenant_with_user


class TenantSerializer(serializers.ModelSerializer):
    """Read serializer — list/retrieve."""
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        model = Tenant
        fields = (
            "id", "email", "full_name", "phone_number", "national_id",
            "emergency_contact_name", "emergency_contact_phone", "status",
            "created_at", "updated_at",
        )
        read_only_fields = fields


class TenantCreateSerializer(serializers.ModelSerializer):
    """
    Creates a User (role=TENANT) + Tenant profile atomically.
    Admin-only endpoint. Creator sets the tenant's password directly —
    no self-registration, no email flow yet (see earlier project decision).
    """
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Tenant
        fields = (
            "id", "email", "username", "first_name", "last_name", "phone_number", "password",
            "national_id", "emergency_contact_name", "emergency_contact_phone", "status",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        return create_tenant_with_user(validated_data=validated_data)


class TenantUpdateSerializer(serializers.ModelSerializer):
    """
    Updates Tenant-specific fields only (not User fields like name/phone —
    that's handled separately via the tenant's own profile endpoint).
    """
    class Meta:
        model = Tenant
        fields = (
            "national_id", "emergency_contact_name",
            "emergency_contact_phone", "status",
        )