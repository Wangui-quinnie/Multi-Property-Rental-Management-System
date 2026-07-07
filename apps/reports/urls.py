from django.urls import path

from .views import landlord_dashboard

app_name = "reports"

urlpatterns = [
    path("landlord-dashboard/", landlord_dashboard, name="landlord_dashboard"),
]