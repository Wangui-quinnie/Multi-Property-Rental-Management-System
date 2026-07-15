from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminOrLandlord
from apps.core.api.responses import success_response

from ..models import Property
from ..filters import PropertyFilter
from ..selectors import get_properties_for_user, get_portfolio_summary_for_user
from ..services import assign_property_owner, archive_property, restore_property
from ..serializers import (
    PropertyCreateSerializer,
    PropertySerializer,
    PropertyUpdateSerializer,
)


class PropertyViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlord]
    lookup_value_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ["name", "code", "location"]
    ordering_fields = ["name", "location", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Property.objects.none()
        include_archived = self.request.query_params.get("archived", "false").lower() == "true"
        return get_properties_for_user(self.request.user, include_archived=include_archived)

    def get_serializer_class(self):
        if self.action == "create":
            return PropertyCreateSerializer
        if self.action in ("update", "partial_update"):
            return PropertyUpdateSerializer
        return PropertySerializer

    def perform_create(self, serializer):
        assign_property_owner(serializer=serializer, user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        # DELETE archives instead of hard-deleting, cascading to units.
        archive_property(instance)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        queryset = get_properties_for_user(request.user, include_archived=True)
        property_obj = get_object_or_404(queryset, pk=pk)
        restore_property(property_obj)
        return success_response(
            data=PropertySerializer(property_obj).data,
            message="Property restored successfully.",
        )

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        summary = get_portfolio_summary_for_user(request.user)
        return success_response(data=summary, message="Portfolio dashboard retrieved successfully.")