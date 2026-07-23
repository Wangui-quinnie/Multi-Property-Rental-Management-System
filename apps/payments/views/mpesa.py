from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from apps.core.api.viewsets import ReadOnlyBaseViewSet
from apps.core.api.responses import success_response, error_response
from rest_framework.exceptions import ValidationError
from apps.tenants.models import Tenant

from ..selectors import get_mpesa_transactions_for_user
from ..services import initiate_stk_push, process_stk_callback
from ..serializers import InitiateStkPushSerializer, MpesaTransactionSerializer, MpesaCallbackSerializer


class MpesaTransactionViewSet(ReadOnlyBaseViewSet):
    """
    Read-only — MpesaTransactions are only ever created via the
    initiate action, and only ever transitioned by the (separate,
    unauthenticated) callback view.
    """

    serializer_class = MpesaTransactionSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import MpesaTransaction
            return MpesaTransaction.objects.none()
        return get_mpesa_transactions_for_user(self.request.user)

    @action(detail=False, methods=["post"], url_path="initiate")
    def initiate(self, request):
        serializer = InitiateStkPushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = get_object_or_404(Tenant, pk=serializer.validated_data["tenant"])

        txn = initiate_stk_push(
            tenant=tenant,
            phone_number=serializer.validated_data["phone_number"],
            amount=serializer.validated_data["amount"],
            user=request.user,
        )

        return success_response(
            data=MpesaTransactionSerializer(txn).data,
            message="STK Push initiated. Awaiting customer confirmation.",
            status_code=201,
        )

class MpesaCallbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=MpesaCallbackSerializer, responses=None, exclude=True)
    def post(self, request):
        body = request.data.get("Body", {}).get("stkCallback", request.data)

        serializer = MpesaCallbackSerializer(data=body)
        if not serializer.is_valid():
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"}, status=200)

        try:
            process_stk_callback(
                checkout_request_id=serializer.validated_data["CheckoutRequestID"],
                result_code=serializer.validated_data["ResultCode"],
                result_description=serializer.validated_data["ResultDesc"],
                mpesa_receipt_number=serializer.validated_data.get("MpesaReceiptNumber"),
            )
        except ValidationError:
            # Unknown checkout_request_id, or some other processing
            # failure on our side. Still return 200 — a non-200 makes
            # Safaricom retry the same callback indefinitely, which
            # won't fix an unknown transaction. Log this in a real
            # deployment for investigation.
            pass

        return Response({"ResultCode": 0, "ResultDesc": "Accepted"}, status=200)