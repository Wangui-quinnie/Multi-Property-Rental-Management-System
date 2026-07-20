from ..models import BillingPeriod


def get_billing_periods_for_user(user):
    """
    BillingPeriod is a shared, system-wide construct — every
    authenticated user (Admin, Landlord, Tenant) can READ the list;
    only Admin can write (enforced at the permission/view level).
    """
    return BillingPeriod.objects.all()