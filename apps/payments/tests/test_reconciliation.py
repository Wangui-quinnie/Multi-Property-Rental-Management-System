import pytest
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease
from apps.payments.models import Payment, MpesaTransaction
from apps.payments.tests.factories import PaymentFactory
from apps.payments.services import (
    allocate_payment_to_invoice,
    initiate_stk_push,
    reconcile_payment,
)

pytestmark = pytest.mark.django_db


def _make_lease_with_invoice(landlord=None, rent_amount=20000):
    from datetime import date

    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=rent_amount)
    billing_period = BillingPeriodFactory(due_date=date.today() + timedelta(days=10))
    invoice = generate_rent_invoice_for_lease(lease, billing_period)
    return lease, invoice, landlord


class TestUnallocatedPayments:
    def test_unallocated_payment_appears_in_dashboard(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, amount=10000, status=Payment.Status.CONFIRMED)

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        assert response.status_code == 200
        entries = response.data["data"]["unallocated_payments"]
        assert len(entries) == 1
        assert entries[0]["payment_id"] == str(payment.id)
        assert float(entries[0]["unallocated_amount"]) == 10000.0

    def test_partially_allocated_payment_shows_remaining_amount(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=20000)
        payment = PaymentFactory(tenant=lease.tenant, amount=20000, status=Payment.Status.CONFIRMED)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=8000, user=landlord)

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        entries = response.data["data"]["unallocated_payments"]
        assert len(entries) == 1
        assert float(entries[0]["total_allocated"]) == 8000.0
        assert float(entries[0]["unallocated_amount"]) == 12000.0

    def test_fully_allocated_payment_excluded(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=15000)
        payment = PaymentFactory(tenant=lease.tenant, amount=15000, status=Payment.Status.CONFIRMED)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=15000, user=landlord)

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        assert response.data["data"]["unallocated_payments"] == []

    def test_pending_payment_excluded_from_unallocated_list(self, authenticated_client):
        """
        Only CONFIRMED payments matter here — a PENDING payment isn't
        confirmed money yet, so it's not "unallocated money," it's
        just not real yet.
        """
        lease, invoice, landlord = _make_lease_with_invoice()
        PaymentFactory(tenant=lease.tenant, amount=10000, status=Payment.Status.PENDING)

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        assert response.data["data"]["unallocated_payments"] == []


class TestStalePendingMpesa:
    def test_recent_pending_transaction_not_flagged(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
        initiate_stk_push(tenant=lease.tenant, phone_number="254712345678", amount=5000, user=landlord)

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        assert response.data["data"]["stale_pending_mpesa"] == []

    def test_stale_pending_transaction_flagged(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
        txn = initiate_stk_push(tenant=lease.tenant, phone_number="254712345678", amount=5000, user=landlord)

        # Backdate created_at past the 1-hour staleness threshold
        MpesaTransaction.objects.filter(pk=txn.pk).update(
            created_at=timezone.now() - timedelta(hours=2)
        )

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        entries = response.data["data"]["stale_pending_mpesa"]
        assert len(entries) == 1
        assert entries[0]["transaction_id"] == str(txn.id)
        assert entries[0]["hours_pending"] >= 2.0

    def test_successful_transaction_never_flagged_as_stale(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
        txn = initiate_stk_push(tenant=lease.tenant, phone_number="254712345678", amount=5000, user=landlord)

        MpesaTransaction.objects.filter(pk=txn.pk).update(
            status=MpesaTransaction.Status.SUCCESS,
            created_at=timezone.now() - timedelta(hours=5),
        )

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        assert response.data["data"]["stale_pending_mpesa"] == []

    def test_failed_transaction_never_flagged_as_stale(self, authenticated_client):
        landlord = LandlordUserFactory()
        unit = UnitFactory(property=PropertyFactory(landlord=landlord))
        lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
        txn = initiate_stk_push(tenant=lease.tenant, phone_number="254712345678", amount=5000, user=landlord)

        MpesaTransaction.objects.filter(pk=txn.pk).update(
            status=MpesaTransaction.Status.FAILED,
            created_at=timezone.now() - timedelta(hours=5),
        )

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        assert response.data["data"]["stale_pending_mpesa"] == []


class TestIntegrityMismatches:
    def test_healthy_system_shows_no_mismatches(self, authenticated_client):
        """
        The expected, normal state — clean() guards should prevent
        any real drift from ever occurring through the service layer.
        """
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=10000)
        payment = PaymentFactory(tenant=lease.tenant, amount=10000, status=Payment.Status.CONFIRMED)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=10000, user=landlord)

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        assert response.data["data"]["integrity_mismatches"] == []

    def test_invoice_amount_paid_drift_detected(self, authenticated_client):
        """
        Simulates data drift that bypasses the service layer entirely
        (e.g. a direct DB edit or Django admin change) — the exact
        scenario this audit exists to catch.
        """
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=10000)
        payment = PaymentFactory(tenant=lease.tenant, amount=10000, status=Payment.Status.CONFIRMED)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=10000, user=landlord)

        # Force a mismatch directly at the DB level, bypassing refresh_totals()
        from apps.billing.models import Invoice
        Invoice.objects.filter(pk=invoice.pk).update(amount_paid=Decimal("5000.00"))

        client = authenticated_client(landlord)
        response = client.get("/api/payments/reconciliation/")

        mismatches = response.data["data"]["integrity_mismatches"]
        assert any(m["type"] == "INVOICE_AMOUNT_PAID_MISMATCH" for m in mismatches)


class TestReconcileAction:
    def test_landlord_reconciles_own_confirmed_payment(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, status=Payment.Status.CONFIRMED)

        client = authenticated_client(landlord)
        response = client.post(f"/api/payments/{payment.id}/reconcile/")

        assert response.status_code == 200
        data = response.data["data"]
        assert data["is_reconciled"] is True
        assert data["reconciled_at"] is not None
        assert data["reconciled_by_name"]

        payment.refresh_from_db()
        assert payment.is_reconciled is True
        assert payment.reconciled_by == landlord

    def test_admin_reconciles_any_payment(self, authenticated_client):
        admin = AdminUserFactory()
        lease, invoice, landlord = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, status=Payment.Status.CONFIRMED)

        client = authenticated_client(admin)
        response = client.post(f"/api/payments/{payment.id}/reconcile/")

        assert response.status_code == 200

    def test_partially_allocated_payment_can_still_be_reconciled(self, authenticated_client):
        """
        Deliberate design choice: reconciliation isn't gated on full
        allocation — a landlord may intentionally reconcile a payment
        that's only partly applied (e.g. tenant overpaid on purpose).
        """
        lease, invoice, landlord = _make_lease_with_invoice(rent_amount=20000)
        payment = PaymentFactory(tenant=lease.tenant, amount=20000, status=Payment.Status.CONFIRMED)
        allocate_payment_to_invoice(payment=payment, invoice=invoice, amount=5000, user=landlord)

        client = authenticated_client(landlord)
        response = client.post(f"/api/payments/{payment.id}/reconcile/")

        assert response.status_code == 200

    def test_reconciling_already_reconciled_payment_rejected(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, status=Payment.Status.CONFIRMED)

        client = authenticated_client(landlord)
        client.post(f"/api/payments/{payment.id}/reconcile/")
        response = client.post(f"/api/payments/{payment.id}/reconcile/")

        assert response.status_code == 400

    def test_reconciling_pending_payment_rejected(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, status=Payment.Status.PENDING)

        client = authenticated_client(landlord)
        response = client.post(f"/api/payments/{payment.id}/reconcile/")

        assert response.status_code == 400

    def test_landlord_cannot_reconcile_unowned_payment(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        lease, invoice, landlord_b = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, status=Payment.Status.CONFIRMED)

        client = authenticated_client(landlord_a)
        response = client.post(f"/api/payments/{payment.id}/reconcile/")

        assert response.status_code == 404  # blocked at queryset scoping


class TestReconciliationPermissionsAndScoping:
    def test_tenant_cannot_view_dashboard(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice()

        client = authenticated_client(lease.tenant.user)
        response = client.get("/api/payments/reconciliation/")

        assert response.status_code == 403

    def test_tenant_cannot_reconcile_payment(self, authenticated_client):
        lease, invoice, landlord = _make_lease_with_invoice()
        payment = PaymentFactory(tenant=lease.tenant, status=Payment.Status.CONFIRMED)

        client = authenticated_client(lease.tenant.user)
        response = client.post(f"/api/payments/{payment.id}/reconcile/")

        assert response.status_code == 403

    def test_landlord_dashboard_scoped_to_own_tenants(self, authenticated_client):
        landlord_a = LandlordUserFactory()
        lease_a, invoice_a, _ = _make_lease_with_invoice(landlord=landlord_a)
        PaymentFactory(tenant=lease_a.tenant, amount=5000, status=Payment.Status.CONFIRMED)

        lease_b, invoice_b, landlord_b = _make_lease_with_invoice()
        PaymentFactory(tenant=lease_b.tenant, amount=99999, status=Payment.Status.CONFIRMED)

        client = authenticated_client(landlord_a)
        response = client.get("/api/payments/reconciliation/")

        entries = response.data["data"]["unallocated_payments"]
        assert len(entries) == 1
        assert float(entries[0]["amount"]) == 5000.0

    def test_admin_dashboard_sees_all_landlords(self, authenticated_client):
        admin = AdminUserFactory()
        lease_a, invoice_a, _ = _make_lease_with_invoice()
        PaymentFactory(tenant=lease_a.tenant, amount=5000, status=Payment.Status.CONFIRMED)

        lease_b, invoice_b, _ = _make_lease_with_invoice()
        PaymentFactory(tenant=lease_b.tenant, amount=8000, status=Payment.Status.CONFIRMED)

        client = authenticated_client(admin)
        response = client.get("/api/payments/reconciliation/")

        assert len(response.data["data"]["unallocated_payments"]) == 2

    def test_unauthenticated_dashboard_request_rejected(self, api_client):
        response = api_client.get("/api/payments/reconciliation/")
        assert response.status_code == 401

    def test_reconciliation_url_not_swallowed_by_payment_detail_route(self, authenticated_client):
        """
        Regression guard, same class as the mpesa/transactions router
        check earlier: 'reconciliation/' must resolve to the dedicated
        dashboard view, not get misrouted into PaymentViewSet's detail
        lookup treating 'reconciliation' as a malformed payment pk.
        """
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)

        response = client.get("/api/payments/reconciliation/")

        assert response.status_code == 200
        assert "unallocated_payments" in response.data["data"]