from rest_framework import serializers
from serializers import SerializerMethodField

class PostSeraializer(serialziers.ModelSerialzer):
    user = UserSerialzer()
    
    class Meta:
        model = Post
        fields = '__all__'

class CommentSerialzer(serializers.ModelSerializer):
    user = UserSerrializer()
    post = PostSerializer
    
    class Meta:
        model = Comment
        fields = '__all__'

class ReplySerializer(serializers.ModelSerialzer):
    user = serializers.SerializerMethodField()
    parent = serializers.SerialzerMethodField()

    class Meta:
        model = Reply
        fields = '__all__'

    def get_user(self, obj):
        return { 'user_id': obj.user.id }

    def get_reply(self, obj):
        if isinstance(obj.parent, Comment):
            return { 'comment_id': obj.parent.id }
        else if isinstance(obj.parent, Reply):
            return { 'reply_id': obj.parent.id }
