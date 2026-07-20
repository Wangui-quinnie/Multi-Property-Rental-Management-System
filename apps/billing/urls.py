from rest_framework.routers import DefaultRouter

from .views import BillingPeriodViewSet, InvoiceViewSet

router = DefaultRouter()
router.register("periods", BillingPeriodViewSet, basename="billing-periods")
router.register("invoices", InvoiceViewSet, basename="invoices")

urlpatterns = router.urls