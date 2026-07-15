from django.db import transaction

from apps.accounts.models import User


def create_tenant_with_user(*, validated_data):
    """
    Atomically creates a User (role=TENANT) and its linked Tenant
    profile. Called only from TenantCreateSerializer.create(), kept
    here rather than inline so the same logic is reusable outside
    the HTTP layer later (e.g. a future bulk-import command).
    """
    from ..models import Tenant

    user_field_names = ["email", "username", "first_name", "last_name", "phone_number"]
    user_fields = {f: validated_data.pop(f, "") for f in user_field_names}
    password = validated_data.pop("password")

    if not user_fields["username"]:
        user_fields["username"] = user_fields["email"].split("@")[0]

    with transaction.atomic():
        user = User(**user_fields, role=User.Role.TENANT)
        user.set_password(password)
        user.save()
        tenant = Tenant.objects.create(user=user, **validated_data)

    return tenant