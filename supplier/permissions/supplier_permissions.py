from rest_framework.permissions import BasePermission


class IsSupplier(BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated and request.user.role == 'supplier':
            return True
        
        return False
