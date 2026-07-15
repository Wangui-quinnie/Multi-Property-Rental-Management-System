# apps/properties/filters.py
import django_filters

from .models import Property, Unit


class PropertyFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")

    class Meta:
        model = Property
        fields = {
            "status": ["exact"],
            "landlord": ["exact"],
        }


class UnitFilter(django_filters.FilterSet):
    min_rent = django_filters.NumberFilter(field_name="rent_amount", lookup_expr="gte")
    max_rent = django_filters.NumberFilter(field_name="rent_amount", lookup_expr="lte")

    class Meta:
        model = Unit
        fields = {
            "status": ["exact"],
            "property": ["exact"],
            "unit_type": ["exact"],
            "floor_number": ["exact"],
        }