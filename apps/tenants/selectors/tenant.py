from ..models import Tenant


def get_tenants_for_user(user):
    """
    Admin and Landlord both see every tenant, regardless of status.
    Admin has full CRUD (enforced by IsAdminWriteLandlordReadOnly);
    Landlords are read-only, needed so they can pick a tenant when
    creating a Lease. No FK from Tenant to Landlord exists by design, so
    this isn't scoped per-property - a Landlord can see any tenant
    system-wide, not just ones already on their own properties.

    Any other role (e.g. Tenant) gets nothing - the permission class
    already blocks them, this is just defense in depth.
    """
    qs = Tenant.objects.select_related("user")
    if user.role in (user.Role.ADMIN, user.Role.LANDLORD):
        return qs.all()
    return Tenant.objects.none()