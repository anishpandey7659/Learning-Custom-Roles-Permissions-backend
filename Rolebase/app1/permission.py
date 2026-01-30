from rest_framework import permissions

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.role != "staff":
            return False
        try:
            return hasattr(user.staff, "doctor")
        except AttributeError:
            return False

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"

class IsAccountant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "staff" and request.user.staff.staff_type == "accountant"