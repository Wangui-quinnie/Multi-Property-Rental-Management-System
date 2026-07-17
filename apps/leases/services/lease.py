from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import PermissionDenied, ValidationError

from ..models import Lease


def assert_landlord_owns_unit(*, unit, user):
    if user.role == user.Role.LANDLORD and unit.property.landlord != user:
        raise PermissionDenied(
            "You cannot create a lease for a unit you don't own."
        )


def create_lease(*, serializer, user):
    unit = serializer.validated_data["unit"]
    assert_landlord_owns_unit(unit=unit, user=user)
    serializer.save()


def update_lease(*, serializer):
    serializer.save()


# apps/leases/services/lease.py
def renew_lease(*, current_lease, new_lease_start_date, rent_amount, deposit_amount, billing_day, user, new_lease_end_date=None):
    """
    Ends the current lease and creates a new one linked via
    renewed_from, preserving each lease term as a distinct historical
    record. Does NOT touch Occupancy or Unit.status — the tenant
    hasn't moved, so there's no occupancy event here.
    """
    if user.role == user.Role.LANDLORD and current_lease.unit.property.landlord != user:
        raise PermissionDenied(
            "You cannot renew a lease for a unit you don't own."
        )

    if current_lease.status != Lease.Status.ACTIVE:
        raise ValidationError(
            {"lease": "Only an ACTIVE lease can be renewed."}
        )

    if hasattr(current_lease, "renewed_to"):
        raise ValidationError(
            {"lease": "This lease has already been renewed."}
        )

    effective_old_end_date = current_lease.lease_end_date or new_lease_start_date

    if new_lease_start_date < effective_old_end_date:
        raise ValidationError(
            {"new_lease_start_date": "New lease cannot start before the current lease ends."}
        )

    with transaction.atomic():
        current_lease.status = Lease.Status.ENDED
        if not current_lease.lease_end_date:
            current_lease.lease_end_date = new_lease_start_date
        current_lease.save(update_fields=["status", "lease_end_date"])

        new_lease = Lease(
            tenant=current_lease.tenant,
            unit=current_lease.unit,
            lease_start_date=new_lease_start_date,
            lease_end_date=new_lease_end_date,
            rent_amount=rent_amount,
            deposit_amount=deposit_amount,
            billing_day=billing_day,
            status=Lease.Status.ACTIVE,
            renewed_from=current_lease,
        )

        try:
            new_lease.clean()
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise ValidationError(exc.message_dict)
            raise ValidationError({"non_field_errors": exc.messages})

        new_lease.save()

    return new_lease