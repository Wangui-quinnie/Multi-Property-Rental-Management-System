from ..models import VacancyPeriod


def open_vacancy_period(*, unit, vacated_at):
    """
    Called when a unit actually becomes vacant (lease termination
    that ended a real Occupancy). Guards against opening a duplicate
    period if one is somehow already open for this unit.
    """
    if VacancyPeriod.objects.filter(unit=unit, occupied_at__isnull=True).exists():
        return None
    return VacancyPeriod.objects.create(unit=unit, vacated_at=vacated_at)


def close_vacancy_period(*, unit, occupied_at):
    """
    Called when a unit becomes occupied again. Closes whichever
    VacancyPeriod is currently open for this unit, if any. If none
    is open (e.g. this is the unit's very first occupancy ever, so
    vacancy was never tracked), this is a no-op — nothing to close.
    """
    open_period = VacancyPeriod.objects.filter(unit=unit, occupied_at__isnull=True).first()
    if open_period is None:
        return None

    open_period.occupied_at = occupied_at
    open_period.save(update_fields=["occupied_at"])
    return open_period