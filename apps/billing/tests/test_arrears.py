import itertools
import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease

pytestmark = pytest.mark.django_db

_offset_counter = itertools.count()


def _make_overdue_invoice_for_lease(lease, days_overdue=10, rent_amount=None):
    """
    Creates an overdue invoice for a specific, already-existing lease
    (unlike earlier test files, this lets multiple invoices share the
    same lease/tenant — needed for arrears aggregation tests).
    """
    offset_days = 400 + (next(_offset_counter) * 40)
    past_start = date.today() - timedelta(days=offset_days)
    billing_period = BillingPeriodFactory(
        start_date=past_start,
        end_date=past_start + timedelta(days=29),
        due_date=date.today() - timedelta(days=days_overdue),
    )
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return invoice


def _make_overdue_lease(landlord=None, tenant_profile=None, rent_amount=20000):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease_kwargs = {"unit": unit, "status": Lease.Status.ACTIVE, "rent_amount": rent_amount}
    if tenant_profile:
        lease_kwargs["tenant"] = tenant_profile
    lease = LeaseFactory(**lease_kwargs)
    return lease, landlord


class TestArrearsByLease:
    def test_single_overdue_invoice_appears_in_by_lease(self, authenticated_client):
        lease, landlord = _make_overdue_lease(rent_amount=20000)
        _make_overdue_invoice_for_lease(lease, days_overdue=10)

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        assert response.status_code == 200
        data = response.data["data"]

        assert len(data["by_lease"]) == 1
        entry = data["by_lease"][0]
        assert entry["lease_id"] == str(lease.id)
        assert float(entry["total_arrears"]) == 20000.0
        assert entry["overdue_invoice_count"] == 1
        assert entry["days_in_arrears"] == 10

    def test_multiple_overdue_invoices_same_lease_sum_together(self, authenticated_client):
        lease, landlord = _make_overdue_lease(rent_amount=15000)
        _make_overdue_invoice_for_lease(lease, days_overdue=40)
        _make_overdue_invoice_for_lease(lease, days_overdue=10)

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        data = response.data["data"]
        assert len(data["by_lease"]) == 1

        entry = data["by_lease"][0]
        assert float(entry["total_arrears"]) == 30000.0  # 15000 * 2
        assert entry["overdue_invoice_count"] == 2
        assert entry["days_in_arrears"] == 40  # oldest invoice wins

    def test_by_lease_sorted_by_days_in_arrears_descending(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease_a, _ = _make_overdue_lease(landlord=landlord, rent_amount=10000)
        lease_b, _ = _make_overdue_lease(landlord=landlord, rent_amount=10000)
        _make_overdue_invoice_for_lease(lease_a, days_overdue=5)
        _make_overdue_invoice_for_lease(lease_b, days_overdue=50)

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        data = response.data["data"]
        assert data["by_lease"][0]["lease_id"] == str(lease_b.id)  # most overdue first
        assert data["by_lease"][1]["lease_id"] == str(lease_a.id)

    def test_fully_paid_invoice_excluded_from_arrears(self, authenticated_client):
        lease, landlord = _make_overdue_lease(rent_amount=10000)
        invoice = _make_overdue_invoice_for_lease(lease, days_overdue=10)

        invoice.amount_paid = invoice.total_amount
        invoice.save()
        invoice.refresh_totals()

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        data = response.data["data"]
        assert len(data["by_lease"]) == 0

    def test_not_yet_due_invoice_excluded_from_arrears(self, authenticated_client):
        lease, landlord = _make_overdue_lease(rent_amount=10000)

        offset_days = 400 + (next(_offset_counter) * 40)
        future_start = date.today() + timedelta(days=offset_days)
        billing_period = BillingPeriodFactory(
            start_date=future_start,
            end_date=future_start + timedelta(days=29),
            due_date=future_start + timedelta(days=5),
        )
        generate_rent_invoice_for_lease(lease, billing_period)

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        assert response.data["data"]["by_lease"] == []


class TestArrearsByTenant:
    def test_tenant_with_multiple_leases_aggregated_together(self, authenticated_client):
        landlord = LandlordUserFactory()
        tenant_profile = TenantFactory()

        lease_1, _ = _make_overdue_lease(landlord=landlord, tenant_profile=tenant_profile, rent_amount=10000)
        lease_2, _ = _make_overdue_lease(landlord=landlord, tenant_profile=tenant_profile, rent_amount=15000)
        _make_overdue_invoice_for_lease(lease_1, days_overdue=10)
        _make_overdue_invoice_for_lease(lease_2, days_overdue=10)

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        data = response.data["data"]
        assert len(data["by_tenant"]) == 1

        entry = data["by_tenant"][0]
        assert entry["tenant_id"] == str(tenant_profile.id)
        assert float(entry["total_arrears"]) == 25000.0
        assert entry["lease_count"] == 2
        assert entry["overdue_invoice_count"] == 2

    def test_by_tenant_sorted_by_total_arrears_descending(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease_a, _ = _make_overdue_lease(landlord=landlord, rent_amount=5000)
        lease_b, _ = _make_overdue_lease(landlord=landlord, rent_amount=50000)
        _make_overdue_invoice_for_lease(lease_a, days_overdue=10)
        _make_overdue_invoice_for_lease(lease_b, days_overdue=10)

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        data = response.data["data"]
        assert float(data["by_tenant"][0]["total_arrears"]) == 50000.0  # highest first


class TestArrearsPortfolioTotal:
    def test_portfolio_total_matches_sum_of_all_arrears(self, authenticated_client):
        landlord = LandlordUserFactory()
        lease_a, _ = _make_overdue_lease(landlord=landlord, rent_amount=10000)
        lease_b, _ = _make_overdue_lease(landlord=landlord, rent_amount=25000)
        _make_overdue_invoice_for_lease(lease_a, days_overdue=10)
        _make_overdue_invoice_for_lease(lease_b, days_overdue=10)

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        data = response.data["data"]
        assert float(data["portfolio_total_arrears"]) == 35000.0
        assert data["leases_in_arrears"] == 2
        assert data["tenants_in_arrears"] == 2

    def test_zero_arrears_returns_empty_clean_response(self, authenticated_client):
        landlord = LandlordUserFactory()

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/arrears/")

        assert response.status_code == 200
        data = response.data["data"]
        assert data["portfolio_total_arrears"] == 0
        assert data["leases_in_arrears"] == 0
        assert data["tenants_in_arrears"] == 0
        assert data["by_lease"] == []
        assert data["by_tenant"] == []


class TestArrearsScoping:
    def test_landlord_sees_only_own_arrears(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        lease_a, _ = _make_overdue_lease(landlord=landlord_a, rent_amount=10000)
        _make_overdue_invoice_for_lease(lease_a, days_overdue=10)

        lease_b, landlord_b = _make_overdue_lease(rent_amount=99999)
        _make_overdue_invoice_for_lease(lease_b, days_overdue=10)

        client = authenticated_client(landlord_a)
        response = client.get("/api/billing/invoices/arrears/")

        data = response.data["data"]
        assert float(data["portfolio_total_arrears"]) == 10000.0
        assert len(data["by_lease"]) == 1

    def test_admin_sees_all_arrears(self, authenticated_client):
        admin = AdminUserFactory()
        lease_a, _ = _make_overdue_lease(rent_amount=10000)
        lease_b, _ = _make_overdue_lease(rent_amount=25000)
        _make_overdue_invoice_for_lease(lease_a, days_overdue=10)
        _make_overdue_invoice_for_lease(lease_b, days_overdue=10)

        client = authenticated_client(admin)
        response = client.get("/api/billing/invoices/arrears/")

        assert float(response.data["data"]["portfolio_total_arrears"]) == 35000.0

    def test_tenant_sees_only_own_arrears(self, authenticated_client):
        tenant_profile = TenantFactory()
        own_lease, _ = _make_overdue_lease(tenant_profile=tenant_profile, rent_amount=8000)
        _make_overdue_invoice_for_lease(own_lease, days_overdue=10)

        other_lease, _ = _make_overdue_lease(rent_amount=99999)
        _make_overdue_invoice_for_lease(other_lease, days_overdue=10)

        client = authenticated_client(tenant_profile.user)
        response = client.get("/api/billing/invoices/arrears/")

        data = response.data["data"]
        assert float(data["portfolio_total_arrears"]) == 8000.0
        assert len(data["by_lease"]) == 1
        assert data["by_lease"][0]["lease_id"] == str(own_lease.id)

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/billing/invoices/arrears/")
        assert response.status_code == 401