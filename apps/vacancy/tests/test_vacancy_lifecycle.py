import pytest
from datetime import date

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.models import Unit
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.leases.services import terminate_lease
from apps.occupancy.services import activate_occupancy
from apps.vacancy.models import VacancyPeriod

pytestmark = pytest.mark.django_db


class TestVacancyLifecycle:
    def test_unit_never_occupied_has_no_vacancy_period(self, authenticated_client):
        """
        Scope limitation, by design: a unit that starts VACANT and has
        never gone through a tracked termination has NO VacancyPeriod
        at all — vacancy tracking begins going forward, not backfilled.
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)

        assert VacancyPeriod.objects.filter(unit=unit).count() == 0

    def test_terminating_lease_opens_vacancy_period(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
        activate_occupancy(lease=lease, user=landlord)

        unit.refresh_from_db()
        assert unit.status == Unit.Status.OCCUPIED
        assert VacancyPeriod.objects.filter(unit=unit).count() == 0  # not yet vacant

        terminate_lease(lease=lease, user=landlord)

        unit.refresh_from_db()
        assert unit.status == Unit.Status.VACANT

        period = VacancyPeriod.objects.get(unit=unit)
        assert period.is_open
        assert period.occupied_at is None
        assert period.vacated_at == date.today()

    def test_activating_new_occupancy_closes_open_vacancy_period(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)

        first_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
        activate_occupancy(lease=first_lease, user=landlord)
        terminate_lease(lease=first_lease, user=landlord)

        period = VacancyPeriod.objects.get(unit=unit)
        assert period.is_open

        unit.refresh_from_db()
        assert unit.status == Unit.Status.VACANT

        second_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
        activate_occupancy(lease=second_lease, user=landlord)

        period.refresh_from_db()
        assert not period.is_open
        assert period.occupied_at == date.today()

        unit.refresh_from_db()
        assert unit.status == Unit.Status.OCCUPIED

    def test_days_vacant_calculated_for_open_period(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
        activate_occupancy(lease=lease, user=landlord)
        terminate_lease(lease=lease, user=landlord)

        period = VacancyPeriod.objects.get(unit=unit)
        assert period.days_vacant == 0  # vacated today, still open

    def test_duplicate_open_period_not_created(self, authenticated_client):
        """
        Defensive guard: open_vacancy_period() should not create a
        second open period for a unit that already has one.
        """
        from apps.vacancy.services import open_vacancy_period

        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))

        open_vacancy_period(unit=unit, vacated_at=date.today())
        open_vacancy_period(unit=unit, vacated_at=date.today())

        assert VacancyPeriod.objects.filter(unit=unit, occupied_at__isnull=True).count() == 1

    def test_closing_with_no_open_period_is_noop(self, authenticated_client):
        """
        A unit's very first-ever occupancy has no prior vacancy to
        close — close_vacancy_period() should silently no-op, not error.
        """
        from apps.vacancy.services import close_vacancy_period

        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))

        result = close_vacancy_period(unit=unit, occupied_at=date.today())

        assert result is None
        assert VacancyPeriod.objects.filter(unit=unit).count() == 0