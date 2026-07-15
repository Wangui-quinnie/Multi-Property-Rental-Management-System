from rest_framework.exceptions import PermissionDenied, ValidationError


def create_unit_for_property(*, serializer, user):
    property_obj = serializer.validated_data["property"]

    if user.role == user.Role.LANDLORD and property_obj.landlord != user:
        raise PermissionDenied(
            "You cannot add units to another landlord's property."
        )

    if property_obj.is_archived:
        raise ValidationError(
            {"property": "Cannot add units to an archived property."}
        )

    serializer.save()