from ..models import Lease


def get_leases_for_user(user):
    """
    ADMIN sees everything. LANDLORD sees leases on units they own.
    TENANT sees only their own lease(s), read-only (enforced at the
    permission/view level, not here).
    """
    queryset = Lease.objects.select_related(
        "tenant__user", "unit__property__landlord"
    )

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(unit__property__landlord=user)

    if user.role == user.Role.TENANT:
        return queryset.filter(tenant__user=user)

    return queryset.none()