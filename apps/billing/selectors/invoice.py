from ..models import Invoice


def get_invoices_for_user(user):
    """
    ADMIN sees all invoices. LANDLORD sees invoices for leases on
    units they own. TENANT sees only their own invoices, read-only.
    """
    queryset = Invoice.objects.select_related(
        "lease__tenant__user", "lease__unit__property__landlord", "billing_period"
    ).prefetch_related("items")

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(lease__unit__property__landlord=user)

    if user.role == user.Role.TENANT:
        return queryset.filter(lease__tenant__user=user)

    return queryset.none()