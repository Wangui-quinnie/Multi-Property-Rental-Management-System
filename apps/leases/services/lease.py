from datetime import date

from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import PermissionDenied, ValidationError

from ..models import Lease
from apps.vacancy.services import open_vacancy_period


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


def renew_lease(*, current_lease, new_lease_start_date, rent_amount, deposit_amount, billing_day, user, new_lease_end_date=None):
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


def terminate_lease(*, lease, user, termination_date=None):
    """
    Ends a lease and, if the tenant had actually moved in, ends the
    linked Occupancy and frees the Unit back to VACANT — all atomic.
    If no Occupancy exists (lease signed but tenant never moved in),
    only the lease itself is ended; there's nothing to revert on the
    Unit since this lease never marked it OCCUPIED.
    """
    from apps.properties.models import Unit
    from apps.occupancy.models import Occupancy

    if user.role == user.Role.LANDLORD and lease.unit.property.landlord != user:
        raise PermissionDenied(
            "You cannot terminate a lease for a unit you don't own."
        )

    if lease.status != Lease.Status.ACTIVE:
        raise ValidationError(
            {"lease": "Only an ACTIVE lease can be terminated."}
        )

    effective_termination_date = termination_date or date.today()

    with transaction.atomic():
        lease.status = Lease.Status.ENDED
        if not lease.lease_end_date or lease.lease_end_date > effective_termination_date:
            lease.lease_end_date = effective_termination_date
        lease.save(update_fields=["status", "lease_end_date"])

        if hasattr(lease, "occupancy") and lease.occupancy.status == Occupancy.Status.ACTIVE:
            occupancy = lease.occupancy
            occupancy.status = Occupancy.Status.ENDED
            occupancy.move_out_date = effective_termination_date
            occupancy.save(update_fields=["status", "move_out_date"])

            unit = lease.unit
            unit.status = Unit.Status.VACANT
            unit.save(update_fields=["status"])

            open_vacancy_period(unit=unit, vacated_at=effective_termination_date)

    return lease