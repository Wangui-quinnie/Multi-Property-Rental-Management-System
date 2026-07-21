import pytest
from unittest.mock import patch
from decimal import Decimal

from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.tenants.tests.factories import TenantFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.payments.models import MpesaTransaction

pytestmark = pytest.mark.django_db


def _tenant_with_lease(landlord=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE)
    return lease.tenant, landlord


class TestStkPushInitiation:
    def test_tenant_initiates_own_payment(self, authenticated_client):
        tenant_profile, landlord = _tenant_with_lease()

        client = authenticated_client(tenant_profile.user)
        response = client.post(
            "/api/payments/mpesa/transactions/initiate/",
            {
                "tenant": str(tenant_profile.id),
                "phone_number": "254712345678",
                "amount": "5000.00",
            },
        )

        assert response.status_code == 201
        data = response.data["data"]
        assert data["status"] == "PENDING"
        assert data["checkout_request_id"]

        assert MpesaTransaction.objects.filter(tenant=tenant_profile).exists()

    def test_landlord_initiates_for_own_tenant(self, authenticated_client):
        tenant_profile, landlord = _tenant_with_lease()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/payments/mpesa/transactions/initiate/",
            {
                "tenant": str(tenant_profile.id),
                "phone_number": "254712345678",
                "amount": "5000.00",
            },
        )

        assert response.status_code == 201

    def test_admin_initiates_for_any_tenant(self, authenticated_client):
        admin = AdminUserFactory()
        tenant_profile, _ = _tenant_with_lease()

        client = authenticated_client(admin)
        response = client.post(
            "/api/payments/mpesa/transactions/initiate/",
            {
                "tenant": str(tenant_profile.id),
                "phone_number": "254712345678",
                "amount": "5000.00",
            },
        )

        assert response.status_code == 201

    def test_landlord_cannot_initiate_for_unrelated_tenant(self, authenticated_client):
        landlord = LandlordUserFactory()
        unrelated_tenant = TenantFactory()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/payments/mpesa/transactions/initiate/",
            {
                "tenant": str(unrelated_tenant.id),
                "phone_number": "254712345678",
                "amount": "5000.00",
            },
        )

        assert response.status_code == 403

    def test_tenant_cannot_initiate_for_another_tenant(self, authenticated_client):
        tenant_profile, _ = _tenant_with_lease()
        other_tenant_profile, _ = _tenant_with_lease()

        client = authenticated_client(tenant_profile.user)
        response = client.post(
            "/api/payments/mpesa/transactions/initiate/",
            {
                "tenant": str(other_tenant_profile.id),
                "phone_number": "254712345678",
                "amount": "5000.00",
            },
        )

        assert response.status_code == 403

    def test_invalid_phone_number_rejected(self, authenticated_client):
        tenant_profile, landlord = _tenant_with_lease()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/payments/mpesa/transactions/initiate/",
            {
                "tenant": str(tenant_profile.id),
                "phone_number": "0712345678",  # wrong format, needs 254 prefix
                "amount": "5000.00",
            },
        )

        assert response.status_code == 400
        assert "phone_number" in response.data

    def test_zero_amount_rejected(self, authenticated_client):
        tenant_profile, landlord = _tenant_with_lease()

        client = authenticated_client(landlord)
        response = client.post(
            "/api/payments/mpesa/transactions/initiate/",
            {
                "tenant": str(tenant_profile.id),
                "phone_number": "254712345678",
                "amount": "0.00",
            },
        )

        assert response.status_code == 400

    def test_safaricom_rejection_surfaces_as_validation_error(self, authenticated_client):
        """
        If Safaricom's API itself rejects the request (non-zero
        ResponseCode), we should surface that as a clean 400, not
        create a transaction record for a push that was never sent.
        """
        tenant_profile, landlord = _tenant_with_lease()

        with patch("apps.payments.services.mpesa.call_safaricom_stk_push") as mock_stk:
            mock_stk.return_value = {
                "ResponseCode": "1",
                "ResponseDescription": "Invalid Amount",
            }

            client = authenticated_client(landlord)
            response = client.post(
                "/api/payments/mpesa/transactions/initiate/",
                {
                    "tenant": str(tenant_profile.id),
                    "phone_number": "254712345678",
                    "amount": "5000.00",
                },
            )

        assert response.status_code == 400
        assert MpesaTransaction.objects.count() == 0

    def test_unauthenticated_request_rejected(self, api_client):
        response = api_client.post("/api/payments/mpesa/transactions/initiate/", {})
        assert response.status_code == 401