from rest_framework.permissions import BasePermission

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