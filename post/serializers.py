from rest_framework import serializers
from shared.serializers import BaseSerializer
from user.serializers import UserSerializer
from .models import (Post, Comment)

class PostSerializer(BaseSerializer):
    user = UserSerializer()

    class Meta:
        model = Post
        fields = '__all__'
    

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Comment
        fields = '__all__'
