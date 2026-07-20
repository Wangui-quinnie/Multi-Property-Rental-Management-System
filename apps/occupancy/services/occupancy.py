from datetime import date

from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.properties.models import Unit

from ..models import Occupancy
from apps.vacancy.services import close_vacancy_period


def activate_occupancy(*, lease, user, move_in_date=None):
    """
    The coordinated occupancy-activation transaction:
      1. Validate the lease belongs to this landlord (admin bypasses).
      2. Validate the lease is ACTIVE.
      3. Validate the unit is currently VACANT.
      4. Create the Occupancy record.
      5. Flip Unit.status to OCCUPIED.
    All steps are atomic — a failure at any point rolls back the whole
    operation, so a unit can never end up OCCUPIED without a matching
    Occupancy record, or vice versa.
    """
    if user.role not in (user.Role.ADMIN, user.Role.LANDLORD):
        raise PermissionDenied(
            "Only Admin or Landlord can activate occupancy."
        )
    
    if user.role == user.Role.LANDLORD and lease.unit.property.landlord != user:
        raise PermissionDenied(
            "You cannot activate occupancy for a unit you don't own."
        )

    if lease.status != lease.Status.ACTIVE:
        raise ValidationError(
            {"lease": "Occupancy can only be activated for an ACTIVE lease."}
        )

    if hasattr(lease, "occupancy"):
        raise ValidationError(
            {"lease": "This lease already has an occupancy record."}
        )

    unit = lease.unit

    if unit.status != Unit.Status.VACANT:
        raise ValidationError(
            {"unit": f"Unit is currently {unit.status}, not VACANT. Cannot activate occupancy."}
        )

    with transaction.atomic():
        occupancy = Occupancy.objects.create(
            lease=lease,
            unit=unit,
            move_in_date=move_in_date or date.today(),
            status=Occupancy.Status.ACTIVE,
        )
        unit.status = Unit.Status.OCCUPIED
        unit.save(update_fields=["status"])

        close_vacancy_period(unit=unit, occupied_at=occupancy.move_in_date)

    return occupancy