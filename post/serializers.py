from rest_framework import serializers
from user.serializers import UserSerializer
from .models import (Post, Comment, Reply)

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    has_next = serializers.SerializerMethodField()
    
    def __init__(self, *args, **kwargs):
        self.has_next = kwargs.pop('has_next') or True
        super().__init__(args, kwargs)

    class Meta:
        model = Post
        fields = '__all__'

    def get_has_next(self, _):
        return self.has_next


class CommentSerialzer(serializers.ModelSerializer):
    user = UserSerializer()
    post = PostSerializer
    
    class Meta:
        model = Comment
        fields = '__all__'

class ReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = '__all__'

    def get_user(self, obj):
        return { 'user_id': obj.user.id }

    def get_reply(self, obj):
        if isinstance(obj.parent, Comment):
            return { 'comment_id': obj.parent.id }
        elif isinstance(obj.parent, Reply):
            return { 'reply_id': obj.parent.id }
