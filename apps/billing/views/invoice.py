from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from apps.core.api.viewsets import ReadOnlyBaseViewSet
from apps.core.api.responses import success_response

from ..models import BillingPeriod
from ..selectors import get_invoices_for_user
from ..services import generate_monthly_rent_invoices
from ..serializers import InvoiceSerializer, GenerateRentInvoicesSerializer


class InvoiceViewSet(ReadOnlyBaseViewSet):
    """
    Read-only — Invoices are only ever created via the generate-rent
    action (and, in step 2, a water-charge action), never directly
    through this API.
    """

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