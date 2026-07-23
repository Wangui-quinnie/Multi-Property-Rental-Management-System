from rest_framework.views import APIView

from apps.core.api.permissions import IsAdminOrLandlord
from apps.core.api.responses import success_response

from ..services import get_reconciliation_dashboard
from ..serializers import ReconciliationDashboardSerializer


class ReconciliationDashboardView(APIView):
    permission_classes = [IsAdminOrLandlord]

    def get(self, request):
        data = get_reconciliation_dashboard(request.user)

        return success_response(
            data=ReconciliationDashboardSerializer(data).data,
            message="Reconciliation dashboard retrieved successfully.",
        )