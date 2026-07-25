from ..models import User


def get_landlords():
    """
    Reference list of every Landlord user, for Admin-facing pickers
    (e.g. choosing a property's owner on creation). Not scoped by
    caller — this selector is only ever reached via an Admin-only view.
    """
    return User.objects.filter(role=User.Role.LANDLORD).order_by("first_name", "last_name", "email")
