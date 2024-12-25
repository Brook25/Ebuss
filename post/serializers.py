from rest_framework import serializers
from user.serializers import UserSerializer
from .models import (Post, Comment, Reply)

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()
        return instance
    

class CommentSerialzer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Comment
        fields = ['text', 'timestamp', 'views', 'likes', 'comments', 'user']

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()
        return instance


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Reply
        fields = '__all__'


    def get_reply(self, obj):
        if isinstance(obj.parent, Comment):
            return { 'comment_id': obj.parent.id }
        elif isinstance(obj.parent, Reply):
            return { 'reply_id': obj.parent.id }
    
    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            if hasattr(instance, attr):
                setattr(instance, attr, val)
        instance.save()
        return instance
