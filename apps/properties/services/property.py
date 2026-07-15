from ..models import Unit

def assign_property_owner(*, serializer, user):
    """
    Saves a new Property. Admins may specify any landlord explicitly
    (already validated by PropertyCreateSerializer.validate_landlord).
    Non-admins (i.e. landlords creating their own property) are
    auto-assigned as the owner.
    """
    if user.role == user.Role.ADMIN:
        serializer.save()
    else:
        serializer.save(landlord=user)

def archive_property(property_obj):
    """
    Archives a property and cascades the archive to all its units
    in a single bulk update. Leases/payments (once they exist) are
    NOT touched — they keep their FK to the archived unit/property,
    preserving historical records exactly as required.
    """
    property_obj.archive()
    Unit.all_objects.filter(property=property_obj).archive()


def restore_property(property_obj):
    """
    Restores a property and cascades the restore to its units,
    symmetric with archive_property.
    """
    property_obj.restore()
    Unit.all_objects.filter(property=property_obj).restore()