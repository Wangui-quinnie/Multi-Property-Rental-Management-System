from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..models import User


class LandlordListSerializer(serializers.ModelSerializer):
    """
    Minimal, read-only shape for landlord picker/reference lists
    (e.g. the Admin "create property" form). Deliberately excludes
    anything beyond what a picker needs.
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "full_name", "email")
        read_only_fields = fields

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return obj.get_full_name()
