import uuid

from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from ..models import MpesaTransaction, Payment
from .payment import _allocate_payment_to_oldest_invoices_core, assert_landlord_manages_tenant


def call_safaricom_stk_push(*, phone_number, amount, account_reference):
    """
    STUBBED — replace with a real Daraja API call once sandbox/production
    credentials are available (see MPESA_* settings).

    Real implementation would:
      1. POST to {DARAJA_BASE_URL}/oauth/v1/generate to get an access token
      2. POST to {DARAJA_BASE_URL}/mpesa/stkpush/v1/processrequest with
         the token, shortcode, passkey-derived password, phone_number,
         amount, and callback_url

    Returns a dict shaped like Safaricom's real response, so callers
    don't need to change when this is swapped for a real call.
    """
    return {
        "MerchantRequestID": str(uuid.uuid4()),
        "CheckoutRequestID": f"ws_CO_{uuid.uuid4().hex[:20]}",
        "ResponseCode": "0",
        "ResponseDescription": "Success. Request accepted for processing",
    }


def initiate_stk_push(*, tenant, phone_number, amount, user):
    if user.role == user.Role.TENANT and tenant.user_id != user.id:
        raise PermissionDenied("You can only initiate M-Pesa payments for yourself.")

    if user.role == user.Role.LANDLORD:
        assert_landlord_manages_tenant(tenant=tenant, user=user)

    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD, user.Role.TENANT):
        raise PermissionDenied("You are not permitted to initiate M-Pesa payments.")

    response = call_safaricom_stk_push(
        phone_number=phone_number,
        amount=amount,
        account_reference=str(tenant.id),
    )

    if response.get("ResponseCode") != "0":
        raise ValidationError(
            {"mpesa": response.get("ResponseDescription", "STK Push request failed.")}
        )

    return MpesaTransaction.objects.create(
        tenant=tenant,
        phone_number=phone_number,
        amount=amount,
        checkout_request_id=response["CheckoutRequestID"],
        merchant_request_id=response["MerchantRequestID"],
        status=MpesaTransaction.Status.PENDING,
    )


@transaction.atomic
def process_stk_callback(*, checkout_request_id, result_code, result_description, mpesa_receipt_number=None):
    """
    Called by the unauthenticated callback view. Idempotent — a
    duplicate callback for an already-processed transaction is a
    no-op. On success, creates a confirmed Payment and immediately
    auto-allocates it to the tenant's oldest outstanding invoices —
    this is a verified system event (Safaricom confirming money was
    received), not a human request, so it bypasses the human
    ownership/permission check entirely and calls the core allocator
    directly.
    """
    try:
        txn = MpesaTransaction.objects.select_for_update().get(
            checkout_request_id=checkout_request_id
        )
    except MpesaTransaction.DoesNotExist:
        raise ValidationError({"checkout_request_id": "Unknown transaction."})

    if txn.status != MpesaTransaction.Status.PENDING:
        return txn  # already processed — idempotent no-op

    txn.result_code = str(result_code)
    txn.result_description = result_description

    if str(result_code) == "0":
        txn.status = MpesaTransaction.Status.SUCCESS
        txn.mpesa_receipt_number = mpesa_receipt_number or ""

        payment = Payment.objects.create(
            tenant=txn.tenant,
            payment_reference=mpesa_receipt_number or txn.checkout_request_id,
            payment_method=Payment.Method.MPESA,
            amount=txn.amount,
            payment_date=txn.updated_at,
            status=Payment.Status.CONFIRMED,
            notes=f"M-Pesa STK Push, checkout ID {txn.checkout_request_id}",
        )
        txn.payment = payment
        txn.save(update_fields=[
            "status", "result_code", "result_description",
            "mpesa_receipt_number", "payment", "updated_at",
        ])

        _allocate_payment_to_oldest_invoices_core(payment=payment)
    else:
        txn.status = (
            MpesaTransaction.Status.CANCELLED if str(result_code) == "1032"
            else MpesaTransaction.Status.FAILED
        )
        txn.save(update_fields=["status", "result_code", "result_description", "updated_at"])

    return txn