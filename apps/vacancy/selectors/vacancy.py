from django.db.models import Avg, F

from ..models import VacancyPeriod


def get_vacancy_periods_for_user(user):
    """
    ADMIN sees everything. LANDLORD sees periods on units they own.
    (Tenant access isn't offered — vacancy data isn't relevant to a
    tenant's own portal.)
    """
    queryset = VacancyPeriod.objects.select_related("unit__property__landlord")

    if user.role == user.Role.ADMIN:
        return queryset

    if user.role == user.Role.LANDLORD:
        return queryset.filter(unit__property__landlord=user)

    return queryset.none()


def get_vacancy_dashboard_for_user(user):
    """
    Currently-vacant units (open periods) with days_vacant, plus
    aggregate stats: count of currently vacant units, and average
    vacancy duration among CLOSED periods (a meaningful "how long do
    vacancies typically last" metric).
    """
    queryset = get_vacancy_periods_for_user(user)

    open_periods = queryset.filter(occupied_at__isnull=True).select_related("unit")
    closed_periods = queryset.filter(occupied_at__isnull=False)

    average_days_closed = closed_periods.annotate(
        duration=F("occupied_at") - F("vacated_at")
    ).aggregate(avg=Avg("duration"))["avg"]

    average_vacancy_days = average_days_closed.days if average_days_closed else 0

    return {
        "currently_vacant_units": open_periods.count(),
        "average_vacancy_duration_days": average_vacancy_days,
        "vacant_units": [
            {
                "unit_id": str(period.unit.id),
                "unit_number": period.unit.unit_number,
                "vacated_at": period.vacated_at,
                "days_vacant": period.days_vacant,
            }
            for period in open_periods
        ],
    }