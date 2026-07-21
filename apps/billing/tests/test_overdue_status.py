import itertools
import pytest
from datetime import date, timedelta

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import Invoice, InvoiceItem, BillingPeriod
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease

pytestmark = pytest.mark.django_db

_offset_counter = itertools.count()


def _make_overdue_invoice(landlord=None, tenant_profile=None, rent_amount=20000):
    """
    Creates an invoice whose billing period is already overdue.
    Each call uses a unique date range (via _offset_counter) to avoid
    colliding with BillingPeriod's unique_billing_period_dates
    constraint when called multiple times in one test.
    """
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease_kwargs = {"unit": unit, "status": Lease.Status.ACTIVE, "rent_amount": rent_amount}
    if tenant_profile:
        lease_kwargs["tenant"] = tenant_profile
    lease = LeaseFactory(**lease_kwargs)

    offset_days = 400 + (next(_offset_counter) * 40)  # far enough back to stay unique and overdue
    past_start = date.today() - timedelta(days=offset_days)
    billing_period = BillingPeriodFactory(
        start_date=past_start,
        end_date=past_start + timedelta(days=29),
        due_date=date.today() - timedelta(days=10),  # always overdue relative to "today"
    )
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return invoice, landlord, lease.tenant


def _force_status(invoice, status):
    """
    Bypasses save()/refresh_totals() entirely — simulates an invoice
    that became overdue with no line-item activity since, which is
    the realistic scenario the batch action is meant to catch up on.
    """
    Invoice.objects.filter(pk=invoice.pk).update(status=status)
    invoice.refresh_from_db()


def _make_not_yet_due_invoice(landlord=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=20000)

    offset_days = 400 + (next(_offset_counter) * 40)
    future_start = date.today() + timedelta(days=offset_days)
    billing_period = BillingPeriodFactory(
        start_date=future_start,
        end_date=future_start + timedelta(days=29),
        due_date=future_start + timedelta(days=5),
    )
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return invoice, landlord


class TestIsOverdueComputedField:
    def test_is_overdue_true_with_stale_unpaid_status(self, authenticated_client):
        """
        is_overdue is computed live at serialization time — it should
        report accurately even when the stored status is stale
        (simulating an invoice nobody has touched since it went overdue).
        """
        invoice, landlord, _ = _make_overdue_invoice()
        _force_status(invoice, Invoice.Status.UNPAID)

        client = authenticated_client(landlord)
        response = client.get(f"/api/billing/invoices/{invoice.id}/")

        assert response.status_code == 200
        assert response.data["is_overdue"] is True
        assert response.data["status"] == "UNPAID"  # stale on purpose

    def test_is_overdue_false_for_not_yet_due_invoice(self, authenticated_client):
        invoice, landlord = _make_not_yet_due_invoice()

        client = authenticated_client(landlord)
        response = client.get(f"/api/billing/invoices/{invoice.id}/")

        assert response.data["is_overdue"] is False

    def test_is_overdue_false_when_fully_paid_despite_past_due_date(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice(rent_amount=10000)

        invoice.amount_paid = invoice.total_amount
        invoice.save()
        invoice.refresh_totals()

        client = authenticated_client(landlord)
        response = client.get(f"/api/billing/invoices/{invoice.id}/")

        assert response.data["is_overdue"] is False
        assert response.data["status"] == "PAID"

    def test_new_invoice_created_past_due_date_is_immediately_overdue(self, authenticated_client):
        """
        Confirms refresh_totals() correctly marks OVERDUE status at
        creation time when the billing period's due date has already
        passed — no batch run needed for this case.
        """
        invoice, landlord, _ = _make_overdue_invoice()
        assert invoice.status == Invoice.Status.OVERDUE


class TestMarkOverdueBatch:
    def test_batch_marks_stale_overdue_invoice(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice()
        _force_status(invoice, Invoice.Status.UNPAID)

        client = authenticated_client(landlord)
        response = client.post("/api/billing/invoices/mark-overdue/")

        assert response.status_code == 200
        assert response.data["data"]["invoices_marked_overdue"] == 1

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.OVERDUE

    def test_rerunning_batch_finds_nothing_new(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice()
        _force_status(invoice, Invoice.Status.UNPAID)

        client = authenticated_client(landlord)
        first = client.post("/api/billing/invoices/mark-overdue/")
        second = client.post("/api/billing/invoices/mark-overdue/")

        assert first.data["data"]["invoices_marked_overdue"] == 1
        assert second.data["data"]["invoices_marked_overdue"] == 0

    def test_not_yet_due_invoice_untouched_by_batch(self, authenticated_client):
        invoice, landlord = _make_not_yet_due_invoice()

        client = authenticated_client(landlord)
        client.post("/api/billing/invoices/mark-overdue/")

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.UNPAID

    def test_fully_paid_invoice_not_marked_overdue(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice(rent_amount=10000)

        invoice.amount_paid = invoice.total_amount
        invoice.save()
        invoice.refresh_totals()
        assert invoice.status == Invoice.Status.PAID

        client = authenticated_client(landlord)
        response = client.post("/api/billing/invoices/mark-overdue/")

        assert response.data["data"]["invoices_marked_overdue"] == 0

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PAID

    def test_admin_batch_covers_all_landlords(self, authenticated_client):
        admin = AdminUserFactory()
        invoice_a, _, _ = _make_overdue_invoice()
        invoice_b, _, _ = _make_overdue_invoice()
        _force_status(invoice_a, Invoice.Status.UNPAID)
        _force_status(invoice_b, Invoice.Status.UNPAID)

        client = authenticated_client(admin)
        response = client.post("/api/billing/invoices/mark-overdue/")

        assert response.data["data"]["invoices_marked_overdue"] == 2

    def test_landlord_batch_scoped_to_own_invoices(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        invoice_a, _, _ = _make_overdue_invoice(landlord=landlord_a)
        invoice_b, landlord_b, _ = _make_overdue_invoice()
        _force_status(invoice_a, Invoice.Status.UNPAID)
        _force_status(invoice_b, Invoice.Status.UNPAID)

        client = authenticated_client(landlord_a)
        response = client.post("/api/billing/invoices/mark-overdue/")

        assert response.data["data"]["invoices_marked_overdue"] == 1

        invoice_a.refresh_from_db()
        invoice_b.refresh_from_db()
        assert invoice_a.status == Invoice.Status.OVERDUE
        assert invoice_b.status == Invoice.Status.UNPAID  # untouched, not landlord_a's

    def test_tenant_cannot_trigger_mark_overdue(self, authenticated_client):
        tenant_profile = TenantFactory()
        invoice, _, _ = _make_overdue_invoice(tenant_profile=tenant_profile)

        client = authenticated_client(tenant_profile.user)
        response = client.post("/api/billing/invoices/mark-overdue/")

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.post("/api/billing/invoices/mark-overdue/")
        assert response.status_code == 401


class TestOverdueStatusSurvivesLineItemChanges:
    def test_applying_late_fee_to_overdue_invoice_keeps_overdue_status(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice()
        assert invoice.status == Invoice.Status.OVERDUE  # already true at creation now

        client = authenticated_client(landlord)
        client.post(
            f"/api/billing/invoices/{invoice.id}/apply-late-fee/",
            {"fee_type": "FIXED", "value": "500.00"},
        )

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.OVERDUE  # still overdue, not reverted
        assert invoice.items.filter(item_type=InvoiceItem.ItemType.PENALTY).count() == 1

    def test_paying_off_overdue_invoice_transitions_to_paid(self, authenticated_client):
        invoice, landlord, _ = _make_overdue_invoice(rent_amount=10000)
        assert invoice.status == Invoice.Status.OVERDUE

        invoice.amount_paid = invoice.total_amount
        invoice.save()
        invoice.refresh_totals()

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PAID