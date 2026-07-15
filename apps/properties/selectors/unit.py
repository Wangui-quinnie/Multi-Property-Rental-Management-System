from django.db.models import Avg, Count, Q, Sum

from ..models import Unit


def get_units_for_user(user, include_archived=False):
    manager = Unit.all_objects if include_archived else Unit.objects

    queryset = manager.select_related("property", "property__landlord")

    if user.role == user.Role.ADMIN:
        return queryset

    return queryset.filter(property__landlord=user)


def get_unit_dashboard_for_user(user):
    queryset = get_units_for_user(user)  # dashboard always excludes archived

    stats = queryset.aggregate(
        total_units=Count("id"),
        occupied_units=Count("id", filter=Q(status="OCCUPIED")),
        vacant_units=Count("id", filter=Q(status="VACANT")),
        maintenance_units=Count("id", filter=Q(status="MAINTENANCE")),
        inactive_units=Count("id", filter=Q(status="INACTIVE")),
        average_rent=Avg("rent_amount"),
        potential_monthly_rent=Sum("rent_amount"),
    )

    total_units = stats["total_units"] or 0
    occupied_units = stats["occupied_units"] or 0
    occupancy_rate = round((occupied_units / total_units) * 100, 2) if total_units else 0.0

    return {
        "total_units": total_units,
        "occupied_units": occupied_units,
        "vacant_units": stats["vacant_units"] or 0,
        "maintenance_units": stats["maintenance_units"] or 0,
        "inactive_units": stats["inactive_units"] or 0,
        "occupancy_rate": occupancy_rate,
        "average_rent": round(stats["average_rent"], 2) if stats["average_rent"] else 0,
        "potential_monthly_rent": stats["potential_monthly_rent"] or 0,
    }