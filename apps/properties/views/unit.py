from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminOrLandlord
from apps.core.api.responses import success_response

from ..models import Unit
from ..filters import UnitFilter
from ..selectors import get_units_for_user, get_unit_dashboard_for_user
from ..services import create_unit_for_property
from ..serializers import (
    UnitCreateSerializer,
    UnitSerializer,
    UnitUpdateSerializer,
)


class UnitViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlord]
    lookup_value_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UnitFilter
    search_fields = ["unit_number", "unit_type"]
    ordering_fields = ["rent_amount", "unit_number", "created_at"]
    ordering = ["unit_number"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Unit.objects.none()
        include_archived = self.request.query_params.get("archived", "false").lower() == "true"
        return get_units_for_user(self.request.user, include_archived=include_archived)

    def get_serializer_class(self):
        if self.action == "create":
            return UnitCreateSerializer
        if self.action in ("update", "partial_update"):
            return UnitUpdateSerializer
        return UnitSerializer

    def perform_create(self, serializer):
        create_unit_for_property(serializer=serializer, user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.archive()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        queryset = get_units_for_user(request.user, include_archived=True)
        unit_obj = get_object_or_404(queryset, pk=pk)
        unit_obj.restore()
        return success_response(
            data=UnitSerializer(unit_obj).data,
            message="Unit restored successfully.",
        )

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        summary = get_unit_dashboard_for_user(request.user)
        return success_response(data=summary, message="Unit dashboard retrieved successfully.")