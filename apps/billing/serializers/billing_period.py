from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import BillingPeriod


class BillingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingPeriod
        fields = ("id", "name", "start_date", "end_date", "due_date", "status", "created_at", "updated_at")
        read_only_fields = fields


class BillingPeriodWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingPeriod
        fields = ("name", "start_date", "end_date", "due_date", "status")

    def validate(self, attrs):
        def field(name, default=None):
            if name in attrs:
                return attrs[name]
            if self.instance is not None:
                return getattr(self.instance, name)
            return default

        temp = BillingPeriod(
            pk=self.instance.pk if self.instance else None,
            name=field("name", ""),
            start_date=field("start_date"),
            end_date=field("end_date"),
            due_date=field("due_date"),
            status=field("status", BillingPeriod.Status.OPEN),
        )

        try:
            temp.clean()
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise serializers.ValidationError(exc.message_dict)
            raise serializers.ValidationError({"non_field_errors": exc.messages})

        return attrs