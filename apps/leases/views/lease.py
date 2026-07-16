from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminOrLandlordWriteTenantReadOnly

from ..selectors import get_leases_for_user
from ..services import create_lease, update_lease
from ..serializers import LeaseSerializer, LeaseCreateSerializer, LeaseUpdateSerializer


class LeaseViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlordWriteTenantReadOnly]

    # DELETE disabled deliberately — lease termination is a dedicated
    # status-transition workflow (roadmap item 5), not a row deletion.
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import Lease
            return Lease.objects.none()
        return get_leases_for_user(self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return LeaseCreateSerializer
        if self.action in ("update", "partial_update"):
            return LeaseUpdateSerializer
        return LeaseSerializer

    def perform_create(self, serializer):
        create_lease(serializer=serializer, user=self.request.user)

    def perform_update(self, serializer):
        update_lease(serializer=serializer)