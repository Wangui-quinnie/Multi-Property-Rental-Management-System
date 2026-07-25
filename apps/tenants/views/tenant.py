from apps.core.api.viewsets import BaseModelViewSet
from apps.core.api.permissions import IsAdmin

from ..selectors import get_tenants_for_user
from ..serializers import TenantSerializer, TenantCreateSerializer, TenantUpdateSerializer


class TenantViewSet(BaseModelViewSet):

    permission_classes = BaseModelViewSet.permission_classes + [IsAdmin]
    # Backs the ?search= param already advertised in the OpenAPI schema
    # via the project-wide SearchFilter backend (config/settings.py) -
    # without this, search was a silent no-op since SearchFilter reads
    # search_fields off the view.
    search_fields = ["user__email", "user__first_name", "user__last_name", "national_id"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import Tenant
            return Tenant.objects.none()
        return get_tenants_for_user(self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return TenantCreateSerializer
        if self.action in ("update", "partial_update"):
            return TenantUpdateSerializer
        return TenantSerializer