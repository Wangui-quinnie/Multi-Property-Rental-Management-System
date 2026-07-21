import pytest
from decimal import Decimal

from apps.accounts.tests.factories import LandlordUserFactory
from apps.properties.tests.factories import PropertyFactory, UnitFactory
from apps.leases.models import Lease
from apps.leases.tests.factories import LeaseFactory
from apps.billing.models import Invoice
from apps.billing.tests.factories import BillingPeriodFactory
from apps.billing.services import generate_rent_invoice_for_lease
from apps.payments.models import MpesaTransaction, Payment
from apps.payments.services import initiate_stk_push

pytestmark = pytest.mark.django_db


def _pending_transaction(landlord=None, rent_amount=10000, amount=None):
    landlord = landlord or LandlordUserFactory()
    unit = UnitFactory(property=PropertyFactory(landlord=landlord))
    lease = LeaseFactory(unit=unit, status=Lease.Status.ACTIVE, rent_amount=rent_amount)
    billing_period = BillingPeriodFactory(status="OPEN")
    invoice = generate_rent_invoice_for_lease(lease, billing_period)

    txn = initiate_stk_push(
        tenant=lease.tenant,
        phone_number="254712345678",
        amount=amount or rent_amount,
        user=landlord,
    )
    return txn, invoice, landlord


def _callback_payload(checkout_request_id, result_code=0, result_desc="Success", receipt="NLJ7RT61SV"):
    payload = {
        "Body": {
            "stkCallback": {
                "CheckoutRequestID": checkout_request_id,
                "ResultCode": result_code,
                "ResultDesc": result_desc,
            }
        }
    }
    if result_code == 0:
        payload["Body"]["stkCallback"]["MpesaReceiptNumber"] = receipt
    return payload


class TestMpesaCallback:
    def test_successful_callback_creates_confirmed_payment(self, api_client):
        txn, invoice, landlord = _pending_transaction(rent_amount=10000)

        response = api_client.post(
            "/api/payments/mpesa/callback/",
            _callback_payload(txn.checkout_request_id),
            format="json",
        )

        assert response.status_code == 200

        txn.refresh_from_db()
        assert txn.status == MpesaTransaction.Status.SUCCESS
        assert txn.mpesa_receipt_number == "NLJ7RT61SV"
        assert txn.payment is not None
        assert txn.payment.status == Payment.Status.CONFIRMED
        assert txn.payment.payment_method == Payment.Method.MPESA

    def test_successful_callback_auto_allocates_to_invoice(self, api_client):
        txn, invoice, landlord = _pending_transaction(rent_amount=10000)

        api_client.post(
            "/api/payments/mpesa/callback/",
            _callback_payload(txn.checkout_request_id),
            format="json",
        )

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PAID
        assert invoice.balance == Decimal("0.00")

    def test_duplicate_callback_is_idempotent(self, api_client):
        txn, invoice, landlord = _pending_transaction(rent_amount=10000)

        first = api_client.post(
            "/api/payments/mpesa/callback/",
            _callback_payload(txn.checkout_request_id),
            format="json",
        )
        second = api_client.post(
            "/api/payments/mpesa/callback/",
            _callback_payload(txn.checkout_request_id),
            format="json",
        )

        assert first.status_code == 200
        assert second.status_code == 200

        assert Payment.objects.count() == 1

    def test_failed_callback_marks_transaction_failed(self, api_client):
        txn, invoice, landlord = _pending_transaction()

        response = api_client.post(
            "/api/payments/mpesa/callback/",
            _callback_payload(txn.checkout_request_id, result_code=1, result_desc="Insufficient funds"),
            format="json",
        )

        assert response.status_code == 200

        txn.refresh_from_db()
        assert txn.status == MpesaTransaction.Status.FAILED
        assert txn.payment is None

    def test_cancelled_callback_marks_transaction_cancelled(self, api_client):
        txn, invoice, landlord = _pending_transaction()

        response = api_client.post(
            "/api/payments/mpesa/callback/",
            _callback_payload(txn.checkout_request_id, result_code=1032, result_desc="Request cancelled by user"),
            format="json",
        )

        assert response.status_code == 200

        txn.refresh_from_db()
        assert txn.status == MpesaTransaction.Status.CANCELLED
        assert txn.payment is None

    def test_unknown_checkout_request_id_still_returns_200(self, api_client):
        response = api_client.post(
            "/api/payments/mpesa/callback/",
            _callback_payload("ws_CO_totally_unknown_id_12345"),
            format="json",
        )

        assert response.status_code == 200
        assert Payment.objects.count() == 0

    def test_malformed_payload_still_returns_200(self, api_client):
        response = api_client.post(
            "/api/payments/mpesa/callback/",
            {"garbage": "data"},
            format="json",
        )

        assert response.status_code == 200

    def test_callback_requires_no_authentication(self, api_client):
        """
        Confirms the callback endpoint is genuinely open — Safaricom
        cannot send an Authorization header, so this must not require one.
        """
        txn, invoice, landlord = _pending_transaction()

        # api_client here is intentionally unauthenticated
        response = api_client.post(
            "/api/payments/mpesa/callback/",
            _callback_payload(txn.checkout_request_id),
            format="json",
        )

        assert response.status_code == 200
        txn.refresh_from_db()
        assert txn.status == MpesaTransaction.Status.SUCCESS