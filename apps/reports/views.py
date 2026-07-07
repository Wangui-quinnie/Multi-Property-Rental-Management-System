from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from apps.properties.models import Property
from apps.reports.services import (
    get_arrears_summary,
    get_occupancy_summary,
    get_property_income_summary,
    get_rent_collection_summary,
    get_water_billing_summary,
)


@staff_member_required
def landlord_dashboard(request):
    property_id = request.GET.get("property") or None

    context = {
        "properties": Property.objects.all().order_by("name"),
        "selected_property_id": property_id,
        "rent_collection": get_rent_collection_summary(property_id=property_id),
        "arrears": get_arrears_summary(property_id=property_id),
        "occupancy": get_occupancy_summary(property_id=property_id),
        "water": get_water_billing_summary(property_id=property_id),
        "property_income": get_property_income_summary(property_id=property_id),
    }

    return render(request, "reports/landlord_dashboard.html", context)