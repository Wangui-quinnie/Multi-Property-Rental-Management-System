from ..models import Payment, PaymentAllocation


def get_payments_for_user(user):
    """
    ADMIN sees all payments. LANDLORD sees payments made by tenants
    who have at least one lease on a unit they own — derived through
    the chain since Tenant has no direct landlord FK, per design.
    TENANT sees only their own payments.
    """
    queryset = Payment.objects.select_related("tenant__user").prefetch_related("allocations")

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(tenant__leases__unit__property__landlord=user).distinct()

    if user.role == user.Role.TENANT:
        return queryset.filter(tenant__user=user)

    return queryset.none()


def get_allocations_for_user(user):
    queryset = PaymentAllocation.objects.select_related(
        "payment__tenant__user", "invoice__lease"
    )

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(payment__tenant__leases__unit__property__landlord=user).distinct()

    if user.role == user.Role.TENANT:
        return queryset.filter(payment__tenant__user=user)

    return queryset.none()