from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class IsAdminOrSalesAgent(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_admin or request.user.is_sales_agent

class IsTechnician(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_technician

class IsAssignedTechnician(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_admin:
            return True
        if not request.user.is_technician:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        if hasattr(obj, 'job'):
            return obj.job.assigned_to == request.user
        return False

class IsJobOwnerOrAssigned(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_admin or request.user.is_sales_agent or request.user.is_technician

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if obj.created_by == request.user:
            return True
        if obj.assigned_to == request.user:
            return True
        return False
