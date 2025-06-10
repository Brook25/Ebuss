from rest_framework.permissions import BasePermission
from restframework import status

class IsChapa(BasePermission):
    
    def has_permission(self, request, view):
        chapa_header = request.headers.get('Chapa-Signature', None)

        if not chapa_header:
            return ('User not Authorzied to access this endpoint.', status=status.HTTP_401_UNAUTHORIZED)

        