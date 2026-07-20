from rest_framework.decorators import action

from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdminOrLandlordWriteTenantReadOnly
from apps.core.api.responses import success_response

from ..selectors import get_leases_for_user
from ..services import create_lease, update_lease, renew_lease, terminate_lease
from ..serializers import (
    LeaseSerializer, LeaseCreateSerializer, LeaseUpdateSerializer,
    LeaseRenewSerializer, LeaseTerminateSerializer,
)


class LeaseViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlordWriteTenantReadOnly]
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

    @action(detail=True, methods=["post"], url_path="renew")
    def renew(self, request, pk=None):
        current_lease = self.get_object()

        serializer = LeaseRenewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_lease = renew_lease(
            current_lease=current_lease,
            user=request.user,
            **serializer.validated_data,
        )

        return success_response(
            data=LeaseSerializer(new_lease).data,
            message="Lease renewed successfully.",
            status_code=201,
        )

    @action(detail=True, methods=["post"], url_path="terminate")
    def terminate(self, request, pk=None):
        lease = self.get_object()

        serializer = LeaseTerminateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        terminated_lease = terminate_lease(
            lease=lease,
            user=request.user,
            termination_date=serializer.validated_data.get("termination_date"),
        )

        return success_response(
            data=LeaseSerializer(terminated_lease).data,
            message="Lease terminated successfully.",
        )