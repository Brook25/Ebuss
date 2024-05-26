from shared import BaseSerializer
from serializers import SerializerMethodField


class PostSeraializer(BaseSerializer):

    
    def get_user(self, obj):
        
        return {'first_name': obj.first_name,
                'last_name': obj.last_name,
                'user_name': obj.user_name
                }

    user = SerializerMethodField(read_only=True)
