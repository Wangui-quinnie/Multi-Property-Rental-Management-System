from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Shared serializer functionality.
    """

    class Meta:
        abstract = True