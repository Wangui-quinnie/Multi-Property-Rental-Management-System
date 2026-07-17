from rest_framework.routers import DefaultRouter

from .views import OccupancyViewSet

router = DefaultRouter()
router.register("", OccupancyViewSet, basename="occupancy")

urlpatterns = router.urls