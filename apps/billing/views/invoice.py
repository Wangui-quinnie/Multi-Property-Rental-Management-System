from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from apps.core.api.viewsets import ReadOnlyBaseViewSet
from apps.core.api.responses import success_response

from ..models import BillingPeriod
from ..selectors import get_invoices_for_user
from ..services import (
    generate_monthly_rent_invoices,
    apply_late_fee,
    apply_late_fees_for_billing_period,
    mark_overdue_invoices,
)
from ..serializers import (
    InvoiceSerializer, GenerateRentInvoicesSerializer,
    ApplyLateFeeSerializer, ApplyLateFeesBatchSerializer,
)


class InvoiceViewSet(ReadOnlyBaseViewSet):

    serializer_class = InvoiceSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import Invoice
            return Invoice.objects.none()
        return get_invoices_for_user(self.request.user)

    @action(detail=False, methods=["post"], url_path="generate-rent")
    def generate_rent(self, request):
        serializer = GenerateRentInvoicesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        billing_period = get_object_or_404(
            BillingPeriod, pk=serializer.validated_data["billing_period"]
        )

        invoices = generate_monthly_rent_invoices(billing_period, request.user)

        return success_response(
            data=InvoiceSerializer(invoices, many=True).data,
            message=f"Generated or refreshed {len(invoices)} invoice(s).",
            status_code=201,
        )

    @action(detail=True, methods=["post"], url_path="apply-late-fee")
    def apply_late_fee_action(self, request, pk=None):
        invoice = self.get_object()

        serializer = ApplyLateFeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        apply_late_fee(
            invoice=invoice,
            user=request.user,
            fee_type=serializer.validated_data["fee_type"],
            value=serializer.validated_data["value"],
        )

        invoice.refresh_from_db()
        return success_response(
            data=InvoiceSerializer(invoice).data,
            message="Late fee applied.",
            status_code=201,
        )

    @action(detail=False, methods=["post"], url_path="apply-late-fees")
    def apply_late_fees_batch(self, request):
        serializer = ApplyLateFeesBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        billing_period = get_object_or_404(
            BillingPeriod, pk=serializer.validated_data["billing_period"]
        )

        items = apply_late_fees_for_billing_period(
            billing_period=billing_period,
            user=request.user,
            fee_type=serializer.validated_data["fee_type"],
            value=serializer.validated_data["value"],
        )

        return success_response(
            data={"late_fees_applied": len(items)},
            message=f"Applied {len(items)} late fee(s).",
            status_code=201,
        )

    @action(detail=False, methods=["post"], url_path="mark-overdue")
    def mark_overdue(self, request):
        updated_count = mark_overdue_invoices(user=request.user)

        return success_response(
            data={"invoices_marked_overdue": updated_count},
            message=f"Marked {updated_count} invoice(s) as overdue.",
        )