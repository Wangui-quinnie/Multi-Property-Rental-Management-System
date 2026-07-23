from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import PaymentViewSet, MpesaTransactionViewSet, MpesaCallbackView, ReconciliationDashboardView

router = DefaultRouter()
router.register("mpesa/transactions", MpesaTransactionViewSet, basename="mpesa-transactions")
router.register("", PaymentViewSet, basename="payments")

urlpatterns = [
    path("mpesa/callback/", MpesaCallbackView.as_view(), name="mpesa-callback"),
    path("reconciliation/", ReconciliationDashboardView.as_view(), name="reconciliation-dashboard"),
] + router.urls