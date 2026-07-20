from django.db.models import ProtectedError

from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminWriteAuthenticatedReadOnly
from apps.core.api.responses import error_response

from ..selectors import get_billing_periods_for_user
from ..serializers import BillingPeriodSerializer, BillingPeriodWriteSerializer


class BillingPeriodViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdminWriteAuthenticatedReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import BillingPeriod
            return BillingPeriod.objects.none()
        return get_billing_periods_for_user(self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BillingPeriodWriteSerializer
        return BillingPeriodSerializer

    def destroy(self, request, *args, **kwargs):
        # WaterMeterReading.billing_period is on_delete=PROTECT — catch
        # that cleanly instead of surfacing a raw 500 (same class of
        # issue we fixed on Property/Unit delete earlier in the project).
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return error_response(
                message="Cannot delete this billing period — it has associated water meter readings or invoices referencing it.",
                status_code=400,
            )