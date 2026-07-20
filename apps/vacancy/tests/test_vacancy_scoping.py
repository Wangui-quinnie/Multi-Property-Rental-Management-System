import pytest
from datetime import date

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.properties.models import Unit
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.leases.services import terminate_lease
from apps.occupancy.services import activate_occupancy

pytestmark = pytest.mark.django_db


def _make_vacant_unit_with_history(landlord=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
    activate_occupancy(lease=lease, user=landlord)
    terminate_lease(lease=lease, user=landlord)
    return unit, landlord


class TestVacancyScoping:
    def test_landlord_sees_only_own_vacancy_periods(self, authenticated_client):
        unit_a, landlord_a = _make_vacant_unit_with_history()
        _make_vacant_unit_with_history()  # unrelated landlord

        client = authenticated_client(landlord_a)
        response = client.get("/api/vacancy/")

        assert response.status_code == 200
        results = response.data["results"]
        assert len(results) == 1
        assert str(results[0]["unit"]) == str(unit_a.id)

    def test_admin_sees_all_vacancy_periods(self, authenticated_client):
        admin = AdminUserFactory()
        _make_vacant_unit_with_history()
        _make_vacant_unit_with_history()

        client = authenticated_client(admin)
        response = client.get("/api/vacancy/")

        assert len(response.data["results"]) == 2

    def test_tenant_blocked_from_vacancy_list(self, authenticated_client):
        tenant = TenantUserFactory()
        client = authenticated_client(tenant)
        response = client.get("/api/vacancy/")

        assert response.status_code == 403

    def test_tenant_blocked_from_vacancy_dashboard(self, authenticated_client):
        tenant = TenantUserFactory()
        client = authenticated_client(tenant)
        response = client.get("/api/vacancy/dashboard/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/vacancy/")
        assert response.status_code == 401

    def test_write_methods_not_exposed(self, authenticated_client):
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)

        response = client.post("/api/vacancy/", {})
        assert response.status_code == 405


class TestVacancyDashboard:
    def test_dashboard_lists_currently_vacant_units(self, authenticated_client):
        unit, landlord = _make_vacant_unit_with_history()

        client = authenticated_client(landlord)
        response = client.get("/api/vacancy/dashboard/")

        assert response.status_code == 200
        data = response.data["data"]

        assert data["currently_vacant_units"] == 1
        assert len(data["vacant_units"]) == 1
        assert data["vacant_units"][0]["unit_id"] == str(unit.id)
        assert data["vacant_units"][0]["days_vacant"] == 0

    def test_dashboard_scoped_by_landlord(self, authenticated_client):
        unit_a, landlord_a = _make_vacant_unit_with_history()
        _make_vacant_unit_with_history()  # unrelated landlord

        client = authenticated_client(landlord_a)
        response = client.get("/api/vacancy/dashboard/")

        assert response.data["data"]["currently_vacant_units"] == 1

    def test_dashboard_drops_count_after_reoccupied(self, authenticated_client):
        unit, landlord = _make_vacant_unit_with_history()

        client = authenticated_client(landlord)
        response = client.get("/api/vacancy/dashboard/")
        assert response.data["data"]["currently_vacant_units"] == 1

        new_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
        activate_occupancy(lease=new_lease, user=landlord)

        response = client.get("/api/vacancy/dashboard/")
        assert response.data["data"]["currently_vacant_units"] == 0

    def test_dashboard_average_vacancy_duration_reflects_closed_periods(self, authenticated_client):
        unit, landlord = _make_vacant_unit_with_history()

        from apps.vacancy.models import VacancyPeriod
        period = VacancyPeriod.objects.get(unit=unit)
        period.vacated_at = date(2026, 1, 1)
        period.occupied_at = date(2026, 1, 11)  # 10-day vacancy
        period.save()

        new_lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, lease_end_date=None)
        activate_occupancy(lease=new_lease, user=landlord)  # this closes any OPEN period; none open now, no-op

        client = authenticated_client(landlord)
        response = client.get("/api/vacancy/dashboard/")

        assert response.data["data"]["average_vacancy_duration_days"] == 10
        assert response.data["data"]["currently_vacant_units"] == 0

    def test_dashboard_zero_vacancies_no_crash(self, authenticated_client):
        landlord = LandlordUserFactory()
        UnitFactory(property=PropertyFactory(landlord=landlord), status=Unit.Status.VACANT)

        client = authenticated_client(landlord)
        response = client.get("/api/vacancy/dashboard/")

        assert response.status_code == 200
        assert response.data["data"]["currently_vacant_units"] == 0
        assert response.data["data"]["average_vacancy_duration_days"] == 0