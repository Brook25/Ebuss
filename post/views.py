from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from .models import (Post, Comment, Reply)
from .serializers import (PostSerializer, CommentSerializer, ReplySerializer)
from django.views import View
from datetime import datetime
from .signals import increment_no_comments
from .serializers import PostSerializer
from rest_framework import Response
from rest_framwork.status import status
import json
from utils import paginate_queryset
# Create your views here.

class News(View):

    def get(self, request, index, *args, **kwargs):

            if index:
                subscriptions = request.user.subscriptions.all()
                all_posts = Post.objects.filter(Q(user__in=subscriptions) | Q(user=request.user)).order_by('-timestamp')
                posts = paginate_queryset(all_posts, request, PostSerializer)

                return Response(posts, status=status.HTTP_200_OK)
            return Response({'message': 'no index provided'},
                        status=400)


class Timeline(View):

    def get(self, request, index, *args, **kwargs):
        my_posts = request.user.posts.all().order_by('-timestamp')
        posts = paginate_queryset(my_posts, request, PostSerializer)

        return Response(posts, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class PostView(View):

    def get(self, request, post, *args, **kwargs):

        id = self.request.GET.get('id', None)
        page = self.request.GET.get('page', 0)
        if not (id and page.isdigit()):
            error = "kw arguement error: check page or id."
            return Response(
                {'message': error}, status=status.HTTP_400_BAD_REQUEST)

        if post == 'p':
            comments = Post.objects.get(pk=id).replies_to.all()
            serializer = CommentSerializer
        elif post == 'c':
            comments = Comment.objects.get(pk=id).replies_to.all()
            serializer = ReplySerializer
        elif post == 'r':
            comments = Reply.object.get(pk=id).replies_to.all()
            serializer = ReplySerializer
        
        comments = paginate_queryset(comments, request, serializer)


        return Response(comments, status=status.HTTP_200_OK)

    def post(self, request, post, *args, **kwargs):

        if post == 'p':
            try:
                data = json.loads(request.body) or {}
                text = data.get('post_data', {}).get('text', '')
                img = request.FILES['image_file']
                #tagged_product = post_data.get('product', None)
                if not (text): # and  tagged_product):
                    return Response({
                            'message': 'post should have a text message and a tagged product.'}, status=status.HTTP_400_BAD_REQUEST)
                post = PostSerializer(data={'user': request.user, 'text': text, 'img': img})
                if post.is_valid():
                    post.create()
                return Response(data={'data': post.id, 'message':
                    'post succefully added'}, status=status.HTTP_200_OK)
            except json.JSONDecodeError as e:
                return Response({'message': 'data could not be parsed'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = json.loads(request.body) or {}
        text = data.get('text', '')
        if not text:
            return Response({'message': 'Text can\'t be empty'}, status=status.HTTP_400_BAD_REQUEST)
        elif post == 'c':
            post_id = data.get('post_id', None)
            post = get_object_or_404(Post, pk=post_id)
            reply_data = {'post': post, 'text': text, 'user': request.user}
            reply = CommentSerializer(data=reply_data)
        elif post == 'r-c':
            comment_id = data.get('comment_id', None)
            comment = get_object_or_404(Comment, pk=comment_id)
            reply_data = {'comment': comment, 'text': text, 'user': request.user}
            reply = ReplySerializer(data=reply_data)
        elif post == 'r-r':
            reply_id = data.get('reply_id', None)
            reply = get_object_or_404(Reply, pk=reply_id)
            reply_data = {'reply': reply, 'text': text, 'user': request.user}
            reply = ReplySerializer(data=reply_data)
            
        if reply.is_valid():
            reply.create()
        
        return Response({'data': comment.id,
                    'message': 'comment successfully added'},
                        status=status.HTTP_200_OK)

    def put(self, request, post, *args, **kwargs):
            data = json.loads(request.body) or {}
            update_data = data.get('update_data', None)

            if not update_data:
                return Response('data to be updated not included', status=status.HTTP_400_BAD_REQUEST)
            
            if post == 'p':
                id = data.get('post_id', None)
                instance = get_object_or_404(Post, pk=id)
                post = PostSerializer(instance=instance, data=update_data, partial=True)

            elif post == 'c':
                id = data.get('comment_id', None)
                instance = get_object_or_404(Comment, pk=id)
                post = CommentSerializer(instance=instance, data=update_data, partial=True)
            elif post == 'r':
                id = data.get('reply_id', None)
                instance = get_object_or_404(Reply, pk=id)
                post = ReplySerializer(data=update_data, partial=True)
            
            if post.is_valid():
                post.save()
            
            return Response({'message': 'comment successfully updated'}, status=status.HTTP_200_OK)
        
    
    def delete(self, request, post, index, *args, **kwargs):
        if not index.is_digit():
            return Response({'message': 'index should be integer'}, status=status.HTTP_400_BAD_REQUEST)
        model = Post if post == 'p' else Comment if post == 'c'
                                 else Reply if post == 'r' else None
        if model:
            post = get_object_or_400(model, pk=index)
            post.delete() 
            return Response({'message': '{} succefully deleted'.format(model.__name__)}, status=HTTP_400_OK)
