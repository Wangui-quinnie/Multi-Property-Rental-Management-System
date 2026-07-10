from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.api.pagination import DefaultPagination
from apps.core.api.permissions import IsAdminOrLandlord

from .models import Property
from .serializers import PropertySerializer, PropertyWriteSerializer

class PropertyViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsAdminOrLandlord,
    ]

    def get_queryset(self):
        user = self.request.user

        queryset = Property.objects.select_related(
            "landlord"
        ).prefetch_related(
            "units"
        )

        if user.role == user.Role.ADMIN:
            return queryset

        return queryset.filter(
            landlord=user
        )

    def get_serializer_class(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            return PropertyWriteSerializer

        return PropertySerializer