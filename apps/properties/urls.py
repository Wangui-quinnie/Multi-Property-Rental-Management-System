from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PropertyViewSet, UnitViewSet

router = DefaultRouter()

router.register(
    "",
    PropertyViewSet,
    basename="properties",
)

router.register(
    "units",
    UnitViewSet,
    basename="units",
)

urlpatterns = [
    path("", include(router.urls)),
]