from rest_framework.exceptions import PermissionDenied


def create_unit_for_property(*, serializer, user):
    """
    Saves a new Unit, guarding against a landlord attaching a unit
    to a property they don't own. Admins bypass this check.
    """
    property_obj = serializer.validated_data["property"]

    if user.role == user.Role.LANDLORD and property_obj.landlord != user:
        raise PermissionDenied(
            "You cannot add units to another landlord's property."
        )

    serializer.save()