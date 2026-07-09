from django.contrib import admin
from django.urls import include, path


urlpatterns = [

    path("admin/", admin.site.urls),
    path(
        "api/auth/",
        include("apps.accounts.urls"),
    ),

    path(
        "api/properties/",
        include("apps.properties.urls"),
    ),

    path(
        "reports/",
        include("apps.reports.urls"),
    ),

]