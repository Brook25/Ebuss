from rest_framework import serializers

class PostSerializer(serializers.Serializer):

    name = serializers.CharField()
    prof_pic = serializers.CharField()
    content = serializers.CharField()
    image = serializers.CharField(allow_null=True)
    comments = serializers.IntegerField()
    likes = serializers.IntegerField()
    shares = serializers.IntegerField()
    posted_at = serializers.CharField()


class PostWithLinkSerializer(serializers.Serializer):

    new_posts = PostSerializer(many=True)
    more_link = serializers.CharField()
