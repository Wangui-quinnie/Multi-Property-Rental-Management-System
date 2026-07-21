from rest_framework.routers import DefaultRouter

from .views import BillingPeriodViewSet, InvoiceViewSet, WaterMeterReadingViewSet

router = DefaultRouter()
router.register("periods", BillingPeriodViewSet, basename="billing-periods")
router.register("invoices", InvoiceViewSet, basename="invoices")
router.register("water-readings", WaterMeterReadingViewSet, basename="water-readings")

urlpatterns = router.urls