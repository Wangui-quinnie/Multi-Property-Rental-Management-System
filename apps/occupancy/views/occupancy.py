from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from apps.core.api.viewsets import ReadOnlyBaseViewSet
from apps.core.api.responses import success_response
from apps.leases.models import Lease

from ..selectors import get_occupancies_for_user
from ..services import activate_occupancy
from ..serializers import OccupancySerializer, OccupancyActivateSerializer


class OccupancyViewSet(ReadOnlyBaseViewSet):
    """
    Read-only list/retrieve (Occupancy records are never edited or
    deleted directly — they're only created via the `activate` action,
    and later ended via a dedicated move-out action in a future
    Vacancy Management workflow).
    """

    serializer_class = OccupancySerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import Occupancy
            return Occupancy.objects.none()
        return get_occupancies_for_user(self.request.user)

    @action(detail=False, methods=["post"], url_path="activate")
    def activate(self, request):
        serializer = OccupancyActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lease = get_object_or_404(Lease, pk=serializer.validated_data["lease"])

        occupancy = activate_occupancy(
            lease=lease,
            user=request.user,
            move_in_date=serializer.validated_data.get("move_in_date"),
        )

        return success_response(
            data=OccupancySerializer(occupancy).data,
            message="Occupancy activated successfully.",
            status_code=201,
        )