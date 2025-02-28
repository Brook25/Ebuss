from rest_framework.permissions import (BasePermission, IsAuthenticated)


class IsAdmin(BasePermission):

    def has_permissions(self, request, view):

        if request.user.is_authenticated and request.user.is_superuser:
            return True
        return False
