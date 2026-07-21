import pytest

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory, TenantUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.payments.models import Payment

pytestmark = pytest.mark.django_db


def _tenant_with_lease(landlord=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
    return lease.tenant, landlord


class TestPaymentCreation:
    def test_landlord_creates_payment_for_own_tenant(self, authenticated_client):
        tenant_profile, landlord = _tenant_with_lease()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/payments/",
            {
                "tenant": str(tenant_profile.id),
                "payment_reference": "PAY-TEST-001",
                "payment_method": "CASH",
                "amount": "15000.00",
                "payment_date": "2026-01-15T10:00:00Z",
            },
        )

        assert response.status_code == 201
        assert Payment.objects.filter(payment_reference="PAY-TEST-001").exists()

    def test_admin_creates_payment_for_any_tenant(self, authenticated_client):
        admin = AdminUserFactory()
        tenant_profile, _ = _tenant_with_lease()

        client = authenticated_client(admin)
        response = client.post(
            "/api/payments/",
            {
                "tenant": str(tenant_profile.id),
                "payment_reference": "PAY-TEST-002",
                "payment_method": "BANK_TRANSFER",
                "amount": "20000.00",
                "payment_date": "2026-01-15T10:00:00Z",
            },
        )

        assert response.status_code == 201

    def test_landlord_cannot_record_payment_for_unrelated_tenant(self, authenticated_client):
        landlord = LandlordUserFactory()
        unrelated_tenant = TenantFactory()  # no lease with this landlord at all

        client = authenticated_client(landlord)
        response = client.post(
            "/api/payments/",
            {
                "tenant": str(unrelated_tenant.id),
                "payment_reference": "PAY-TEST-003",
                "payment_method": "CASH",
                "amount": "10000.00",
                "payment_date": "2026-01-15T10:00:00Z",
            },
        )

        assert response.status_code == 403
        assert not Payment.objects.filter(payment_reference="PAY-TEST-003").exists()

    def test_tenant_cannot_create_payment(self, authenticated_client):
        tenant = TenantUserFactory()

        client = authenticated_client(tenant)
        response = client.post(
            "/api/payments/",
            {
                "tenant": str(tenant.id),
                "payment_reference": "PAY-TEST-004",
                "payment_method": "CASH",
                "amount": "5000.00",
                "payment_date": "2026-01-15T10:00:00Z",
            },
        )

        assert response.status_code == 403

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.get("/api/payments/")
        assert response.status_code == 401

    def test_duplicate_payment_reference_rejected(self, authenticated_client):
        tenant_profile, landlord = _tenant_with_lease()

        client = authenticated_client(landlord)
        payload = {
            "tenant": str(tenant_profile.id),
            "payment_reference": "PAY-DUP-001",
            "payment_method": "CASH",
            "amount": "10000.00",
            "payment_date": "2026-01-15T10:00:00Z",
        }
        client.post("/api/payments/", payload)
        response = client.post("/api/payments/", payload)

        assert response.status_code == 400

    def test_patch_disabled(self, authenticated_client):
        tenant_profile, landlord = _tenant_with_lease()
        client = authenticated_client(landlord)
        create = client.post(
            "/api/payments/",
            {
                "tenant": str(tenant_profile.id),
                "payment_reference": "PAY-TEST-005",
                "payment_method": "CASH",
                "amount": "10000.00",
                "payment_date": "2026-01-15T10:00:00Z",
            },
        )
        payment = Payment.objects.get(payment_reference="PAY-TEST-005")

        response = client.patch(f"/api/payments/{payment.id}/", {"amount": "99999.00"})
        assert response.status_code == 405

    def test_delete_disabled(self, authenticated_client):
        from apps.payments.tests.factories import PaymentFactory

        tenant_profile, landlord = _tenant_with_lease()
        payment = PaymentFactory(tenant=tenant_profile)

        client = authenticated_client(landlord)
        response = client.delete(f"/api/payments/{payment.id}/")
        assert response.status_code == 405

    def test_landlord_sees_only_payments_for_own_tenants(self, authenticated_client):
        from apps.payments.tests.factories import PaymentFactory

        tenant_a, landlord_a = _tenant_with_lease()
        tenant_b, landlord_b = _tenant_with_lease()

        PaymentFactory(tenant=tenant_a)
        PaymentFactory(tenant=tenant_b)

        client = authenticated_client(landlord_a)
        response = client.get("/api/payments/")

        results = response.data["results"]
        assert len(results) == 1
        assert str(results[0]["tenant"]) == str(tenant_a.id)

    def test_admin_sees_all_payments(self, authenticated_client):
        from apps.payments.tests.factories import PaymentFactory

        admin = AdminUserFactory()
        tenant_a, _ = _tenant_with_lease()
        tenant_b, _ = _tenant_with_lease()
        PaymentFactory(tenant=tenant_a)
        PaymentFactory(tenant=tenant_b)

        client = authenticated_client(admin)
        response = client.get("/api/payments/")

        assert len(response.data["results"]) == 2