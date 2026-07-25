from rest_framework import generics
from drf_spectacular.utils import extend_schema

from apps.core.api.permissions import IsAdmin
from apps.core.api.responses import success_response
from apps.core.api.schema import enveloped_response

from ..selectors import get_landlords
from ..serializers import LandlordListSerializer


class LandlordListView(generics.ListAPIView):
    """
    Admin-only reference list of Landlord users, used to populate the
    landlord picker when an Admin creates a Property on someone else's
    behalf (PropertyCreateSerializer.landlord). Landlords never need
    this list themselves — they're auto-assigned as the owner.

    Deliberately unpaginated: this is a lookup/reference list for a
    picker, not a browsable collection.
    """
    permission_classes = [IsAdmin]
    serializer_class = LandlordListSerializer
    pagination_class = None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return get_landlords().none()
        return get_landlords()

    @extend_schema(responses=enveloped_response("LandlordListEnvelope", LandlordListSerializer, many=True))
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response(
            data=serializer.data,
            message="Landlords retrieved successfully.",
        )
