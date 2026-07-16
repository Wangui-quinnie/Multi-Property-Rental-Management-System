from rest_framework.routers import DefaultRouter

from .views import LeaseViewSet

router = DefaultRouter()
router.register("", LeaseViewSet, basename="leases")

urlpatterns = router.urls