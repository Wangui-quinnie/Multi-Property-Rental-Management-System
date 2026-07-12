from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .pagination import DefaultPagination


class BaseModelViewSet(ModelViewSet):
    """
    Shared defaults for API viewsets across the project.

    Provides:
      - permission_classes: [IsAuthenticated] (a safe universal floor —
        every endpoint requires login; nothing is publicly accessible
        by accident)
      - pagination_class: DefaultPagination

    Role-specific restrictions (IsAdminOrLandlord, IsTenant, object-level
    permissions, etc.) are NOT included here — they vary per resource
    and must be added explicitly on each subclass, e.g.:

        class PropertyViewSet(BaseModelViewSet):
            permission_classes = BaseModelViewSet.permission_classes + [IsAdminOrLandlord]
    """
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination