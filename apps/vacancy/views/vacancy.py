from rest_framework.decorators import action

from apps.core.api.viewsets import ReadOnlyBaseViewSet
from apps.core.api.permissions import IsAdminOrLandlord
from apps.core.api.responses import success_response

from ..selectors import get_vacancy_periods_for_user, get_vacancy_dashboard_for_user
from ..serializers import VacancyPeriodSerializer


class VacancyPeriodViewSet(ReadOnlyBaseViewSet):
    """
    Read-only — VacancyPeriod records are only ever created/closed
    internally by the Lease Termination and Occupancy Activation
    services, never directly through this API.
    """

    permission_classes = ReadOnlyBaseViewSet.permission_classes + [IsAdminOrLandlord]
    serializer_class = VacancyPeriodSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            from ..models import VacancyPeriod
            return VacancyPeriod.objects.none()
        return get_vacancy_periods_for_user(self.request.user)

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        summary = get_vacancy_dashboard_for_user(request.user)
        return success_response(
            data=summary,
            message="Vacancy dashboard retrieved successfully.",
        )