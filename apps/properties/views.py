from django.db.models import Count, Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.core.api.pagination import DefaultPagination
from apps.core.api.permissions import IsAdminOrLandlord

from .filters import PropertyFilter
from .models import Property, Unit
from .serializers import (
    PropertyCreateSerializer,
    PropertySerializer,
    PropertyUpdateSerializer,
    UnitCreateSerializer,
    UnitSerializer,
    UnitUpdateSerializer,
)


class PropertyViewSet(ModelViewSet):

    permission_classes = [
        IsAuthenticated,
        IsAdminOrLandlord,
    ]

    pagination_class = DefaultPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = PropertyFilter

    search_fields = [
        "name",
        "code",
        "location",
    ]

    ordering_fields = [
        "name",
        "location",
        "created_at",
    ]

    ordering = [
        "name",
    ]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Property.objects
            .select_related("landlord")
            .annotate(
                total_units=Count("units"),
                occupied_units=Count(
                    "units",
                    filter=Q(units__status="OCCUPIED"),
                ),
                vacant_units=Count(
                    "units",
                    filter=Q(units__status="VACANT"),
                ),
            )
            .order_by("name")
        )

        if user.role == user.Role.ADMIN:
            return queryset

        return queryset.filter(landlord=user)

    def get_serializer_class(self):
        if self.action == "create":
            return PropertyCreateSerializer

        if self.action in ("update", "partial_update"):
            return PropertyUpdateSerializer

        return PropertySerializer

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == user.Role.ADMIN:
            serializer.save()
        else:
            serializer.save(landlord=user)

    def perform_update(self, serializer):
        serializer.save()


class UnitViewSet(ModelViewSet):

    permission_classes = [
        IsAuthenticated,
        IsAdminOrLandlord,
    ]

    pagination_class = DefaultPagination

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Unit.objects
            .select_related("property", "property__landlord")
        )

        if user.role == user.Role.ADMIN:
            return queryset

        return queryset.filter(property__landlord=user)

    def get_serializer_class(self):
        if self.action == "create":
            return UnitCreateSerializer

        if self.action in ("update", "partial_update"):
            return UnitUpdateSerializer

        return UnitSerializer

    def perform_create(self, serializer):
        user = self.request.user
        property_obj = serializer.validated_data["property"]

        if user.role == user.Role.LANDLORD and property_obj.landlord != user:
            raise PermissionDenied(
                "You cannot add units to another landlord's property."
            )

        serializer.save()

    def perform_update(self, serializer):
        serializer.save()