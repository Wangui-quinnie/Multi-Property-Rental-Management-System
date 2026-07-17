from ..models import Occupancy


def get_occupancies_for_user(user):
    """
    ADMIN sees everything. LANDLORD sees occupancies on units they own.
    TENANT sees their own occupancy record(s), read-only.
    """
    queryset = Occupancy.objects.select_related(
        "lease__tenant__user", "unit__property__landlord"
    )

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(unit__property__landlord=user)

    if user.role == user.Role.TENANT:
        return queryset.filter(lease__tenant__user=user)

    return queryset.none()