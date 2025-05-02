from rest_framework import serializers
from shared.serializers import BaseSerializer
from user.serializers import UserSerializer
from rest_framework.relations import PrimaryKeyRelatedField
from .models import (Post, Comment)
from user.models import User



class PostSerializer(BaseSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    post = PrimaryKeyRelatedField(queryset=Post.objects.all(), allow_null=True)
    parent_comment = PrimaryKeyRelatedField(queryset=Comment.objects.all(), allow_null=True)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
    

class CommentSerializer(BaseSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    
    def create(self):
        comment = super().create()
        post_id, parent_comment_id = self.validated_data.get('post', None), self.validated_data.get('parent_comment', None)
        parent_obj = Post.objects.get(post_id) if post_id else Comment.objects.get(parent_comment_id)
        parent_obj.comments = F('comments') + 1
        parent_obj.save(updated_fields=['comments'])
        return comment
    

    def validate(self, attrs):
        super().validate(attrs)
        
        if (attrs.get('post') and attrs.get('parent_comment')) or (not attrs.get('post') and not attrs.get('parent_comment')):
            raise ValidationError('One of \'post\' or \'parent_comment\' fields must be null.')
        
        return attrs 
   
    class Meta:
        model = Comment
        fields = '__all__'
