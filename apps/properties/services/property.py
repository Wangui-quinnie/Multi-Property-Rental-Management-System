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