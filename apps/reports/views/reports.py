from datetime import datetime

from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from apps.core.api.permissions import IsAdminOrLandlord
from apps.core.api.responses import success_response

from ..selectors import (
    get_rent_billed_vs_collected,
    get_water_billing_summary,
    get_cash_flow_trend,
    get_landlord_summary,
)
from ..serializers import RentReportSerializer, WaterReportSerializer, CashFlowEntrySerializer


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


class RentReportView(APIView):
    permission_classes = [IsAdminOrLandlord]

    @extend_schema(responses=RentReportSerializer)
    def get(self, request):
        data = get_rent_billed_vs_collected(
            request.user,
            start_date=_parse_date(request.query_params.get("start_date")),
            end_date=_parse_date(request.query_params.get("end_date")),
        )
        return success_response(data=RentReportSerializer(data).data, message="Rent report retrieved.")


class WaterReportView(APIView):
    permission_classes = [IsAdminOrLandlord]

    @extend_schema(responses=WaterReportSerializer)
    def get(self, request):
        data = get_water_billing_summary(
            request.user,
            start_date=_parse_date(request.query_params.get("start_date")),
            end_date=_parse_date(request.query_params.get("end_date")),
        )
        return success_response(data=WaterReportSerializer(data).data, message="Water report retrieved.")


class CashFlowReportView(APIView):
    permission_classes = [IsAdminOrLandlord]

    @extend_schema(responses=CashFlowEntrySerializer(many=True))
    def get(self, request):
        months = int(request.query_params.get("months", 6))
        data = get_cash_flow_trend(request.user, months=months)
        return success_response(
            data=CashFlowEntrySerializer(data, many=True).data,
            message="Cash flow trend retrieved.",
        )


class LandlordSummaryView(APIView):
    permission_classes = [IsAdminOrLandlord]

    @extend_schema(responses=None)
    def get(self, request):
        data = get_landlord_summary(
            request.user,
            start_date=_parse_date(request.query_params.get("start_date")),
            end_date=_parse_date(request.query_params.get("end_date")),
        )
        return success_response(data=data, message="Landlord summary retrieved.")