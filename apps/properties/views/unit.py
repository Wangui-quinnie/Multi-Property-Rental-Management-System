from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminOrLandlord

from ..selectors import get_units_for_user
from ..services import create_unit_for_property
from ..serializers import (
    UnitCreateSerializer,
    UnitSerializer,
    UnitUpdateSerializer,
)


class UnitViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlord]

    def get_queryset(self):
        return get_units_for_user(self.request.user)

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