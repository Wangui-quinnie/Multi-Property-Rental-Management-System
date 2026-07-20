from rest_framework.routers import DefaultRouter
from .views import VacancyPeriodViewSet

router = DefaultRouter()
router.register("", VacancyPeriodViewSet, basename="vacancy")
urlpatterns = router.urls