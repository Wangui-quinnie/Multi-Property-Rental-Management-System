from ..models import MpesaTransaction


def get_mpesa_transactions_for_user(user):
    queryset = MpesaTransaction.objects.select_related("tenant__user", "payment")

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(tenant__leases__unit__property__landlord=user).distinct()

    if user.role == user.Role.TENANT:
        return queryset.filter(tenant__user=user)

    return queryset.none()