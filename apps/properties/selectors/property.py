from django.db.models import Count, Q

from ..models import Property


def get_properties_for_user(user):
    """
    Returns the base Property queryset, annotated with unit counts,
    scoped to what this user is allowed to see.

    ADMIN sees everything. LANDLORD sees only properties they own.
    """
    queryset = (
        Property.objects
        .select_related("landlord")
        .annotate(
            total_units=Count("units"),
            occupied_units=Count(
                "units", filter=Q(units__status="OCCUPIED")
            ),
            vacant_units=Count(
                "units", filter=Q(units__status="VACANT")
            ),
        )
        .order_by("name")
    )

    if user.role == user.Role.ADMIN:
        return queryset

    return queryset.filter(landlord=user)