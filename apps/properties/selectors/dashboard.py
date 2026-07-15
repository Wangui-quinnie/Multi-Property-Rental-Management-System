from django.db.models import Count, Q, Sum

from ..models import Unit
from .property import get_properties_for_user


def get_portfolio_summary_for_user(user):
    """
    Aggregate dashboard stats across every property this user can see.
    Scoped identically to get_properties_for_user (ADMIN sees all,
    LANDLORD sees only their own).
    """
    properties = get_properties_for_user(user)
    total_properties = properties.count()

    units = Unit.objects.filter(property__in=properties)

    stats = units.aggregate(
        total_units=Count("id"),
        occupied_units=Count("id", filter=Q(status="OCCUPIED")),
        vacant_units=Count("id", filter=Q(status="VACANT")),
        maintenance_units=Count("id", filter=Q(status="MAINTENANCE")),
        potential_monthly_rent=Sum("rent_amount"),
    )

    total_units = stats["total_units"] or 0
    occupied_units = stats["occupied_units"] or 0

    occupancy_rate = (
        round((occupied_units / total_units) * 100, 2) if total_units else 0.0
    )

    return {
        "total_properties": total_properties,
        "total_units": total_units,
        "occupied_units": occupied_units,
        "vacant_units": stats["vacant_units"] or 0,
        "maintenance_units": stats["maintenance_units"] or 0,
        "occupancy_rate": occupancy_rate,
        "potential_monthly_rent": stats["potential_monthly_rent"] or 0,
    }