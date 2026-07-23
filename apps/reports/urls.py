from django.urls import path

from .views import RentReportView, WaterReportView, CashFlowReportView, LandlordSummaryView

urlpatterns = [
    path("rent/", RentReportView.as_view(), name="rent-report"),
    path("water/", WaterReportView.as_view(), name="water-report"),
    path("cash-flow/", CashFlowReportView.as_view(), name="cash-flow-report"),
    path("landlord-summary/", LandlordSummaryView.as_view(), name="landlord-summary"),
]