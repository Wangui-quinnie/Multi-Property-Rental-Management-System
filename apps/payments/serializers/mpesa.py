from rest_framework import serializers

from decimal import Decimal
from ..models import MpesaTransaction


class InitiateStkPushSerializer(serializers.Serializer):
    tenant = serializers.UUIDField()
    phone_number = serializers.RegexField(
        regex=r"^254[71]\d{8}$",
        error_messages={"invalid": "Phone number must be in the format 2547XXXXXXXX or 2541XXXXXXXX."},
    )
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("1"))


class MpesaTransactionSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.user.get_full_name", read_only=True)

    class Meta:
        model = MpesaTransaction
        fields = (
            "id", "tenant", "tenant_name", "phone_number", "amount",
            "checkout_request_id", "mpesa_receipt_number", "status",
            "result_description", "payment", "created_at", "updated_at",
        )
        read_only_fields = fields


class MpesaCallbackSerializer(serializers.Serializer):
    """
    Shaped to match Safaricom's actual STK Push callback payload
    structure (nested under Body.stkCallback). Only the fields we
    actually use are extracted; anything else Safaricom sends is
    ignored rather than rejected, since their payload format has
    changed before and we shouldn't hard-fail on unrecognized extras.
    """
    CheckoutRequestID = serializers.CharField()
    ResultCode = serializers.IntegerField()
    ResultDesc = serializers.CharField()
    MpesaReceiptNumber = serializers.CharField(required=False, allow_blank=True)