import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import Invoice, InvoiceItem
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease

pytestmark = pytest.mark.django_db


def _make_overdue_invoice(landlord=None, tenant_profile=None, rent_amount=20000):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease_kwargs = {"unit": unit, "status": Lease.Status.ACTIVE, "rent_amount": rent_amount}
    if tenant_profile:
        lease_kwargs["tenant"] = tenant_profile
    lease = LeaseFactory(**lease_kwargs)

    past_start = date.today() - timedelta(days=60)
    billing_period = BillingPeriodFactory(
        start_date=past_start,
        end_date=past_start + timedelta(days=29),
        due_date=date.today() - timedelta(days=10),  # overdue
    )
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return invoice, landlord, lease.tenant


def _make_not_yet_due_invoice(landlord=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=20000)

    future_start = date.today() + timedelta(days=30)
    billing_period = BillingPeriodFactory(
        start_date=future_start,
        end_date=future_start + timedelta(days=29),
        due_date=future_start + timedelta(days=5),  # not yet due
    )
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return invoice, landlord


class TestManualLateFee:
    def test_landlord_applies_fixed_fee_to_own_overdue_invoice(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice()

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "FIXED", "value": "500.00"},
        )

        assert response.status_code == 201

        invoice.refresh_from_db()
        penalty_item = invoice.items.get(item_type=InvoiceItem.ItemType.PENALTY)
        assert penalty_item.amount == Decimal("500.00")
        assert float(invoice.total_amount) == 20000.0 + 500.0

    def test_landlord_applies_percentage_fee(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice(rent_amount=20000)

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "PERCENTAGE", "value": "5"},
        )

        assert response.status_code == 201

        invoice.refresh_from_db()
        penalty_item = invoice.items.get(item_type=InvoiceItem.ItemType.PENALTY)
        assert penalty_item.amount == Decimal("1000.00")  # 5% of 20000

    def test_admin_can_apply_fee_to_any_invoice(self, authenticated_client):
        admin = AdminUserFactory()
        invoice, landlord, _ = _make_overdue_invoice()

        client = authenticated_client(admin)
        response = client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "FIXED", "value": "300.00"},
        )

        assert response.status_code == 201

    def test_duplicate_fee_same_day_rejected(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice()

        client = authenticated_client(landlord)
        client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "FIXED", "value": "500.00"},
        )
        response = client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "FIXED", "value": "500.00"},
        )

        assert response.status_code == 400

        invoice.refresh_from_db()
        assert invoice.items.filter(item_type=InvoiceItem.ItemType.PENALTY).count() == 1

    def test_cannot_apply_fee_to_not_yet_due_invoice(self, authenticated_client):
        invoice, landlord = _make_not_yet_due_invoice()

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "FIXED", "value": "500.00"},
        )

        assert response.status_code == 400
        assert invoice.items.filter(item_type=InvoiceItem.ItemType.PENALTY).count() == 0

    def test_landlord_cannot_apply_fee_to_unowned_invoice(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        invoice, landlord_b, _ = _make_overdue_invoice()

        client = authenticated_client(landlord_a)
        response = client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "FIXED", "value": "500.00"},
        )

        # Blocked at queryset scoping (get_object) before the action body runs
        assert response.status_code == 404

    def test_tenant_cannot_apply_fee(self, authenticated_client):
        tenant_profile = TenantFactory()
        invoice, _, _ = _make_overdue_invoice(tenant_profile=tenant_profile)

        client = authenticated_client(tenant_profile.user)
        response = client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "FIXED", "value": "500.00"},
        )

        assert response.status_code == 403

    def test_invalid_fee_type_rejected(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice()

        client = authenticated_client(landlord)
        response = client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "BOGUS", "value": "500.00"},
        )

        assert response.status_code == 400


class TestBatchLateFees:
    def test_batch_applies_only_to_overdue_invoices_in_period(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=15000)

        past_start = date.today() - timedelta(days=60)
        billing_period = BillingPeriodFactory(
            start_date=past_start,
            end_date=past_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=10),
        )
        overdue_invoice = generate_rent_invoice_for_lease(lease, billing_period)

        # A second, unrelated NOT-overdue invoice in a different period should be untouched
        not_due_invoice, _ = _make_not_yet_due_invoice(landlord=landlord)

        client = authenticated_client(landlord)
        response = client.post(
            "/api/billing/invoices/apply-late-fees/",
            {"billing_period": str(billing_period.id), "fee_type": "FIXED", "value": "500.00"},
        )

        assert response.status_code == 201
        assert response.data["data"]["late_fees_applied"] == 1

        overdue_invoice.refresh_from_db()
        assert overdue_invoice.items.filter(item_type=InvoiceItem.ItemType.PENALTY).count() == 1

        not_due_invoice.refresh_from_db()
        assert not_due_invoice.items.filter(item_type=InvoiceItem.ItemType.PENALTY).count() == 0

    def test_batch_scoped_to_landlords_own_leases(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        landlord_b = LandlordUserFactory()

        past_start = date.today() - timedelta(days=60)
        billing_period = BillingPeriodFactory(
            start_date=past_start,
            end_date=past_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=10),
        )

        lease_a = LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord_a)),
            status=Lease.Status.ACTIVE,
        )
        lease_b = LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord_b)),
            status=Lease.Status.ACTIVE,
        )
        generate_rent_invoice_for_lease(lease_a, billing_period)
        generate_rent_invoice_for_lease(lease_b, billing_period)

        client = authenticated_client(landlord_a)
        response = client.post(
            "/api/billing/invoices/apply-late-fees/",
            {"billing_period": str(billing_period.id), "fee_type": "FIXED", "value": "500.00"},
        )

        assert response.data["data"]["late_fees_applied"] == 1  # only landlord_a's invoice

    def test_admin_batch_applies_across_all_landlords(self, authenticated_client):
        admin = AdminUserFactory()

        past_start = date.today() - timedelta(days=60)
        billing_period = BillingPeriodFactory(
            start_date=past_start,
            end_date=past_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=10),
        )

        lease_a = LeaseFactory(status=Lease.Status.ACTIVE)
        lease_b = LeaseFactory(status=Lease.Status.ACTIVE)
        generate_rent_invoice_for_lease(lease_a, billing_period)
        generate_rent_invoice_for_lease(lease_b, billing_period)

        client = authenticated_client(admin)
        response = client.post(
            "/api/billing/invoices/apply-late-fees/",
            {"billing_period": str(billing_period.id), "fee_type": "FIXED", "value": "500.00"},
        )

        assert response.data["data"]["late_fees_applied"] == 2

    def test_rerunning_batch_same_day_applies_zero(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)

        past_start = date.today() - timedelta(days=60)
        billing_period = BillingPeriodFactory(
            start_date=past_start,
            end_date=past_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=10),
        )
        generate_rent_invoice_for_lease(lease, billing_period)

        client = authenticated_client(landlord)
        first = client.post(
            "/api/billing/invoices/apply-late-fees/",
            {"billing_period": str(billing_period.id), "fee_type": "FIXED", "value": "500.00"},
        )
        second = client.post(
            "/api/billing/invoices/apply-late-fees/",
            {"billing_period": str(billing_period.id), "fee_type": "FIXED", "value": "500.00"},
        )

        assert first.data["data"]["late_fees_applied"] == 1
        assert second.data["data"]["late_fees_applied"] == 0  # already fee'd today, skipped not errored

    def test_tenant_cannot_trigger_batch(self, authenticated_client):
        tenant_profile = TenantFactory()
        billing_period = BillingPeriodFactory()

        client = authenticated_client(tenant_profile.user)
        response = client.post(
            "/api/billing/invoices/apply-late-fees/",
            {"billing_period": str(billing_period.id), "fee_type": "FIXED", "value": "500.00"},
        )

        assert response.status_code == 403

    def test_paid_invoice_excluded_from_batch(self, authenticated_client):
        """
        An overdue invoice with balance == 0 (fully paid) should not
        receive a late fee — is_invoice_overdue() requires balance > 0.
        """
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=10000)

        past_start = date.today() - timedelta(days=60)
        billing_period = BillingPeriodFactory(
            start_date=past_start,
            end_date=past_start + timedelta(days=29),
            due_date=date.today() - timedelta(days=10),
        )
        invoice = generate_rent_invoice_for_lease(lease, billing_period)

        # Manually simulate full payment (Payment app doesn't exist yet — Phase 5)
        invoice.amount_paid = invoice.total_amount
        invoice.save()
        invoice.refresh_totals()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/billing/invoices/apply-late-fees/",
            {"billing_period": str(billing_period.id), "fee_type": "FIXED", "value": "500.00"},
        )

        assert response.data["data"]["late_fees_applied"] == 0