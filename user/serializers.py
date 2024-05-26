from rest_framework import serializers
from .models import (Notification, History)
from shared.serialziers import BaseSerializer

'''class UserSerializer(BaseSerializer):

        def get_links(self, obj):

            if obj.__class__.__name__ in ['Product', 'User']:
                return super().get_links(obj)
            return None
'''
