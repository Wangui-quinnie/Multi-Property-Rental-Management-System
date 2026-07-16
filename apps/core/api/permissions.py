from rest_framework.permissions import BasePermission, SAFE_METHODS

#Admin only permission class
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )
#Landlord only permission class
class IsLandlord(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "LANDLORD"
        )
#Tenant only permission class
class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "TENANT"
        )
    
#Admin or Landlord only permission class
#This keeps permission logic centralized in the model.
class IsAdminOrLandlord(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin_or_landlord
        )
# Admin or Landlord write, Tenant read-only permission class
class IsAdminOrLandlordWriteTenantReadOnly(BasePermission):
    """
    View-level gate: write methods require Admin or Landlord.
    Read methods (GET) are allowed through for any authenticated user;
    actual visibility (including Tenant-sees-own-only) is enforced by
    queryset scoping in get_queryset(), not here.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin_or_landlord