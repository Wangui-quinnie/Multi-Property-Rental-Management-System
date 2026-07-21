from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminOrLandlordWriteTenantReadOnly
from apps.core.api.responses import success_response

from apps.billing.models import Invoice

from ..selectors import get_payments_for_user
from ..services import (
    create_payment,
    allocate_payment_to_invoice,
    allocate_payment_to_oldest_invoices,
    remove_allocation,
    get_receipt_data,
)
from ..serializers import PaymentSerializer, PaymentCreateSerializer, AllocateToInvoiceSerializer, ReceiptSerializer


class PaymentViewSet(BaseModelViewSet):
    """
    Create + read only — Payments are immutable financial records
    once created (no update/destroy). Admin and Landlord have full
    access; Tenant has read-only access (list/retrieve/receipt) to
    their own payments, enforced via IsAdminOrLandlordWriteTenantReadOnly
    plus the existing queryset scoping in get_payments_for_user.
    """

    http_method_names = ["get", "post", "head", "options"]
    permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlordWriteTenantReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import Payment
            return Payment.objects.none()
        return get_payments_for_user(self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        create_payment(serializer=serializer, user=self.request.user)

    @action(detail=True, methods=["post"], url_path="allocate")
    def allocate(self, request, pk=None):
        payment = self.get_object()

        serializer = AllocateToInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invoice = get_object_or_404(Invoice, pk=serializer.validated_data["invoice"])

        allocate_payment_to_invoice(
            payment=payment,
            invoice=invoice,
            amount=serializer.validated_data["amount"],
            user=request.user,
        )

        payment.refresh_from_db()
        return success_response(
            data=PaymentSerializer(payment).data,
            message="Payment allocated to invoice.",
            status_code=201,
        )

    @action(detail=True, methods=["post"], url_path="allocate-oldest")
    def allocate_oldest(self, request, pk=None):
        payment = self.get_object()

        allocations = allocate_payment_to_oldest_invoices(payment=payment, user=request.user)

        payment.refresh_from_db()
        return success_response(
            data=PaymentSerializer(payment).data,
            message=f"Allocated to {len(allocations)} invoice(s).",
            status_code=201,
        )

    @action(detail=True, methods=["post"], url_path="allocations/(?P<allocation_id>[^/.]+)/remove")
    def remove_allocation_action(self, request, pk=None, allocation_id=None):
        payment = self.get_object()
        allocation = get_object_or_404(payment.allocations, pk=allocation_id)

        remove_allocation(allocation=allocation, user=request.user)

        payment.refresh_from_db()
        return success_response(
            data=PaymentSerializer(payment).data,
            message="Allocation removed.",
        )

    @action(detail=True, methods=["get"], url_path="receipt")
    def receipt(self, request, pk=None):
        payment = self.get_object()

        data = get_receipt_data(payment=payment)

        return success_response(
            data=ReceiptSerializer(data).data,
            message="Receipt retrieved successfully.",
        )