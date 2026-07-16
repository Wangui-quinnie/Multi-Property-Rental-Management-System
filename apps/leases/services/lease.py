from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import PermissionDenied


def assert_landlord_owns_unit(*, unit, user):
    """
    Guards against a Landlord creating a lease for a unit they don't
    own. Admins bypass this check entirely.
    """
    if user.role == user.Role.LANDLORD and unit.property.landlord != user:
        raise PermissionDenied(
            "You cannot create a lease for a unit you don't own."
        )


def create_lease(*, serializer, user):
    unit = serializer.validated_data["unit"]
    assert_landlord_owns_unit(unit=unit, user=user)
    serializer.save()


def update_lease(*, serializer):
    serializer.save()