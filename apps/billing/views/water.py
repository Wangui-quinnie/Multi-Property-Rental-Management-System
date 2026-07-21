from rest_framework.decorators import action

from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminOrLandlord
from apps.core.api.responses import success_response

from ..selectors import get_water_readings_for_user
from ..services import create_water_reading, update_water_reading, delete_water_reading, apply_water_charge
from ..serializers import WaterMeterReadingSerializer, WaterMeterReadingCreateSerializer, WaterMeterReadingUpdateSerializer


class WaterMeterReadingViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlord]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import WaterMeterReading
            return WaterMeterReading.objects.none()
        return get_water_readings_for_user(self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return WaterMeterReadingCreateSerializer
        if self.action in ("update", "partial_update"):
            return WaterMeterReadingUpdateSerializer
        return WaterMeterReadingSerializer

    def perform_create(self, serializer):
        create_water_reading(serializer=serializer, user=self.request.user)

    def perform_update(self, serializer):
        update_water_reading(serializer=serializer)

    def perform_destroy(self, instance):
        delete_water_reading(water_reading=instance)

    @action(detail=True, methods=["post"], url_path="apply-charge")
    def apply_charge(self, request, pk=None):
        water_reading = self.get_object()

        invoice_item = apply_water_charge(water_reading=water_reading, user=request.user)

        return success_response(
            data=WaterMeterReadingSerializer(water_reading).data,
            message="Water charge applied to invoice.",
            status_code=201,
        )