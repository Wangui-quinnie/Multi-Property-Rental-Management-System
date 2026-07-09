from rest_framework.viewsets import ModelViewSet

from apps.core.api.pagination import DefaultPagination
from apps.core.api.responses import success_response

from .models import Property
from .serializers import PropertySerializer


class PropertyViewSet(ModelViewSet):

    serializer_class = PropertySerializer

    queryset = Property.objects.all()

    pagination_class = DefaultPagination