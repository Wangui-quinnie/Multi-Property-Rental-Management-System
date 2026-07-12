from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminOrLandlord

from ..filters import PropertyFilter
from ..selectors import get_properties_for_user
from ..services import assign_property_owner
from ..serializers import (
    PropertyCreateSerializer,
    PropertySerializer,
    PropertyUpdateSerializer,
)


class PropertyViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlord]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ["name", "code", "location"]
    ordering_fields = ["name", "location", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return get_properties_for_user(self.request.user)

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