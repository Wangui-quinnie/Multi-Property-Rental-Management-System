from ..models import WaterMeterReading


def get_water_readings_for_user(user):
    """
    ADMIN sees all readings. LANDLORD sees readings for units they
    own. No Tenant access — reading entry/correction is a Landlord/
    Admin operation; tenants see the resulting invoice, not the raw
    meter data.
    """
    queryset = WaterMeterReading.objects.select_related(
        "unit__property__landlord", "billing_period", "invoice_item"
    )

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(unit__property__landlord=user)

    return queryset.none()