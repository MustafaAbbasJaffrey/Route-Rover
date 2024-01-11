from rest_framework import permissions
from user_management.models import Profile

class IsDriver(permissions.BasePermission):
    message = 'Only drivers are allowed to perform this action. '
    def has_permission(self, request, view):
        return request.user.is_authenticated \
            and \
                Profile.objects.filter(user=request.user, role__name="driver").exists()

class IsGuardian(permissions.BasePermission):
    message = 'Only guardians are allowed to perform this action. '
    def has_permission(self, request, view):
        return request.user.is_authenticated \
            and \
                Profile.objects.filter(user=request.user, role__name="guardian").exists()
    
class IsAdmin(permissions.BasePermission):
    message = 'Only admin users are allowed to perform this action. '
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
            request.user.is_superuser