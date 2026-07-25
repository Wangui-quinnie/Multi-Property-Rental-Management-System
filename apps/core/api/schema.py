from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


def enveloped_response(name, serializer, many=False):
    """
    Builds an OpenAPI-accurate response schema for endpoints that
    return the standard {success, message, data} envelope produced
    by success_response(), instead of the bare serializer body.

    Without this, @extend_schema(responses=SomeSerializer) describes
    the response as IF it were the serializer body directly, which is
    wrong for anything wrapped in success_response — the generated
    frontend types then claim `response.data` IS the object, when in
    reality it's one level deeper at `response.data.data`. This same
    mismatch already existed on the properties app's `restore` and
    `dashboard` custom actions (never fixed there); use this helper
    going forward instead of leaving new endpoints with the same gap.

    Usage:
        @extend_schema(responses=enveloped_response("LandlordListEnvelope", LandlordListSerializer, many=True))
        def list(self, request, *args, **kwargs): ...
    """
    data_field = serializer(many=True) if many else serializer()
    return inline_serializer(
        name=name,
        fields={
            "success": serializers.BooleanField(),
            "message": serializers.CharField(),
            "data": data_field,
        },
    )
