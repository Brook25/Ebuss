from rest_framework.permissions import BasePermission
from restframework import status
from rest_framework.
import os
import hlib
import hmac


class IsChapa(BasePermission):
    
    def has_permission(self, request, view):
        chapa_hash = request.headers.get('Chapa-Signature', None)

        if not chapa_header:
            return Response('User not Authorzied to access this endpoint.', status=status.HTTP_401_UNAUTHORIZED)

       if not request.data:
           return Response('No payload data provided.', status=status.HTTP_400_BAD_REQUEST)
        
        secret_key = os.env.get('CHAPA_SECRET_KEY', None)
        
        if not secret_key:
            return Response('authorization couldn\'t be processed.', status.HTTP_501_SERVER_ERROR)
        
        hash_obj = hmac.new(secret_key.encode('utf-8'), request.body, hlib.sha256)
        hash = has_obj.hexdigest()

        if hash != chapa_hash:
            return Response('User not Authorized. Invalid Hash Key.', status=status.HTTP_401_UNAUTHORIZED)


