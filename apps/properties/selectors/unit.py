from ..models import Unit


def get_units_for_user(user):
    """
    Returns the base Unit queryset, scoped to what this user is
    allowed to see. ADMIN sees everything. LANDLORD sees only units
    on properties they own.
    """
    queryset = Unit.objects.select_related("property", "property__landlord")

    if user.role == user.Role.ADMIN:
        return queryset

    return queryset.filter(property__landlord=user)