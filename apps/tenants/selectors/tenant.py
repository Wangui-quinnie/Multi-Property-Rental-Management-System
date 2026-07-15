from ..models import Tenant


def get_tenants_for_user(user):
    """
    Admin-only for now. No FK from Tenant to Landlord exists by design —
    ownership will be derived through Landlord -> Property -> Unit ->
    Lease -> Tenant once the Lease module exists.
    """
    return Tenant.objects.select_related("user").all()