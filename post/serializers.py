from rest_framework import serializers
from shared.serializers import BaseSerializer
from user.serializers import UserSerializer
from .models import (Post, Comment, Reply)

class PostSerializer(BaseSerializer):
    user = UserSerializer()

    class Meta:
        model = Post
        fields = '__all__'
    

class CommentSerialzer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Comment
        fields = ['text', 'timestamp', 'views', 'likes', 'comments', 'user']


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Reply
        fields = '__all__'


