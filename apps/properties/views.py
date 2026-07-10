from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.api.pagination import DefaultPagination
from apps.core.api.permissions import IsAdminOrLandlord

from .models import Property
from .serializers import (
    PropertyCreateSerializer,
    PropertySerializer,
    PropertyUpdateSerializer,
)


class PropertyViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsAdminOrLandlord,
    ]

    pagination_class = DefaultPagination

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Property.objects
            .select_related("landlord")
            .prefetch_related("units")
            .order_by("name")
        )

        if user.role == user.Role.ADMIN:
            return queryset

        return queryset.filter(
            landlord=user
        )

    def get_serializer_class(self):
        if self.action == "create":
            return PropertyCreateSerializer

        if self.action in (
            "update",
            "partial_update",
        ):
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