from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/properties/", include("apps.properties.urls")),
    path("reports/", include("apps.reports.urls")),
    path("api/tenants/", include("apps.tenants.urls")),
    path("api/leases/", include("apps.leases.urls")),
    path("api/occupancy/", include("apps.occupancy.urls")),
    path("api/vacancy/", include("apps.vacancy.urls")),
    path("api/billing/", include("apps.billing.urls")),
    path("api/payments/", include("apps.payments.urls")),

    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]