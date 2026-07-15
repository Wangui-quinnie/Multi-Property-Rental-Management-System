from django.db.models import Count, Q, Sum

from ..models import Property


def get_properties_for_user(user, include_archived=False):
    """
    Returns the base Property queryset, annotated with unit counts
    and rent potential, scoped to what this user is allowed to see.

    By default, archived properties are excluded (Property.objects
    already filters them out). Pass include_archived=True to use
    Property.all_objects instead, surfacing archived rows too.
    """
    manager = Property.all_objects if include_archived else Property.objects

    queryset = (
        manager
        .select_related("landlord")
        .annotate(
            total_units=Count("units"),
            occupied_units=Count("units", filter=Q(units__status="OCCUPIED")),
            vacant_units=Count("units", filter=Q(units__status="VACANT")),
            maintenance_units=Count("units", filter=Q(units__status="MAINTENANCE")),
            potential_monthly_rent=Sum("units__rent_amount"),
        )
        .order_by("name")
    )

    if user.role == user.Role.ADMIN:
        return queryset

    return queryset.filter(landlord=user)