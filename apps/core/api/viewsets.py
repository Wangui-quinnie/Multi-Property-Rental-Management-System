from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from .pagination import DefaultPagination


class BaseModelViewSet(ModelViewSet):
    """
    Shared defaults for full-CRUD viewsets.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination


class ReadOnlyBaseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    """
    Shared defaults for list/retrieve-only viewsets that expose their
    real mutations through custom @action methods instead of the
    standard create/update/delete verbs (e.g. Occupancy, which is only
    ever created via the guarded `activate` action).
    """
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination