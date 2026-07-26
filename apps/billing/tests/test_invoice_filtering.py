# Covers the InvoiceViewSet.filterset_fields fix - added so the frontend
# can show status tabs (Unpaid/Overdue/Paid/...) and a billing-period-
# scoped invoice list (Phase 4, Billing UI).
import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import Invoice
from apps.billing.services import generate_rent_invoice_for_lease
from apps.billing.tests.factories import BillingPeriodFactory

pytestmark = pytest.mark.django_db


class TestInvoiceFiltering:
    def test_filter_by_status(self, authenticated_client):
        admin = AdminUserFactory()
        billing_period = BillingPeriodFactory()

        lease = LeaseFactory(status=Lease.Status.ACTIVE)
        invoice = generate_rent_invoice_for_lease(lease, billing_period)
        invoice.status = Invoice.Status.PAID
        invoice.save(update_fields=["status"])

        other_lease = LeaseFactory(status=Lease.Status.ACTIVE)
        generate_rent_invoice_for_lease(other_lease, BillingPeriodFactory())

        client = authenticated_client(admin)
        response = client.get("/api/billing/invoices/?status=PAID")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(invoice.id)

    def test_filter_by_billing_period(self, authenticated_client):
        admin = AdminUserFactory()
        billing_period = BillingPeriodFactory()

        lease = LeaseFactory(status=Lease.Status.ACTIVE)
        invoice = generate_rent_invoice_for_lease(lease, billing_period)

        other_lease = LeaseFactory(status=Lease.Status.ACTIVE)
        generate_rent_invoice_for_lease(other_lease, BillingPeriodFactory())  # different period

        client = authenticated_client(admin)
        response = client.get(f"/api/billing/invoices/?billing_period={billing_period.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(invoice.id)

    def test_filter_by_lease(self, authenticated_client):
        admin = AdminUserFactory()
        billing_period = BillingPeriodFactory()

        lease = LeaseFactory(status=Lease.Status.ACTIVE)
        invoice = generate_rent_invoice_for_lease(lease, billing_period)

        other_lease = LeaseFactory(status=Lease.Status.ACTIVE)
        generate_rent_invoice_for_lease(other_lease, billing_period)

        client = authenticated_client(admin)
        response = client.get(f"/api/billing/invoices/?lease={lease.id}")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(invoice.id)

    def test_landlord_filtering_still_scoped_to_own_leases(self, authenticated_client):
        landlord = LandlordUserFactory()
        billing_period = BillingPeriodFactory()

        own_lease = LeaseFactory(
            unit=UnitFactory(property=PropertyFactory(landlord=landlord)),
            status=Lease.Status.ACTIVE,
        )
        own_invoice = generate_rent_invoice_for_lease(own_lease, billing_period)
        own_invoice.status = Invoice.Status.PAID
        own_invoice.save(update_fields=["status"])

        other_lease = LeaseFactory(status=Lease.Status.ACTIVE)
        other_invoice = generate_rent_invoice_for_lease(other_lease, billing_period)
        other_invoice.status = Invoice.Status.PAID
        other_invoice.save(update_fields=["status"])

        client = authenticated_client(landlord)
        response = client.get("/api/billing/invoices/?status=PAID")

        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["id"] == str(own_invoice.id)
