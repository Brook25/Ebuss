from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from post.models import (Post, Comment, Reply)
from django.views import View
from datetime import datetime
from .signals import increment_no_comments
from .serializers import PostSerializer
from django.http import JsonResponse
import json
from utils import paginate_queryset
# Create your views here.

class News(View):

    def get(self, request, index, *args, **kwargs):

            if index:
                subscriptions = request.user.subscriptions.all()
                all_posts = Post.objects.filter(Q(user__in=subscriptions) | Q(user=user)).order_by('-timestamp')
                posts = paginate_queryset(posts_from_subs, request, PostSerializer)

                return Response(post, status=HTTP_200_OK)
            return Response({'message': 'no index provided'},
                        status=400)


class Timeline(View):

    def get(self, request, index, *args, **kwargs):
        my_posts = request.user.posts.all().order_by('-timestamp')
        posts = paginate_queryset(posts_from_subs, request, PostSerializer)

        return Response(posts, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class PostView(View):

    def get(self, request, post, *args, **kwargs):

        id = self.request.GET.get('id', None)
        page = self.request.GET.get('page', 0)
        if not (id and page):
            error = "kw arguement error: check page or id."
            return JsonResponse(
                {'message': error}, status=400)

        if post == 'p':
            comments = Post.objects.filter(pk=id).first().replies_to.all()
            serializer = CommentSerializer
        elif post == 'c':
            comments = Comment.objects.filter(pk=id).first().replies_to.all()
            serializer = ReplySerializer
        else:
            comments = Reply.object.filter(pk=id).first().replies_to.all()
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
                            'message': 'post should have a text message and a tagged product.'}, status=400)
                post = PostSerializer(data={'user': request.user, 'text': text, 'img': img})
                if post.is_valid():
                    post.create()
                return Response(data={'data': post.id, 'message':
                    'post succefully added'}, status=status.HTTP_200_OK)
            except json.JSONDecodeError as e:
                return JsonResponse(data={'data': None,
                    'message': 'data could not be parsed'}, status=400)
        
        elif post == 'c':
            data = json.loads(request.body) or {}
            post_id = data.get('post_id', None)
            comment_id = data.get('comment_id', None)
            text = data.get('text', '')
            if post_id and text:
                reply_data = {'post': post, 'text': text, 'user': request.user}
                reply = CommentSerializer(data=reply_data)
            elif comment_id and text:
                reply_data = {'comment': comment, 'text': text, 'user': request.user}
                reply = ReplySerializer(data=reply_data)
            else:
                return Response({'message': 'proper key words missing.'}, status=401)
            if reply.is_valid():
                reply.create()
            return Response({'data': comment.id,
                    'message': 'comment successfully added'},
                        status=HTTP_200_OK)

    def put(self, request, post, *args, **kwargs):
            data = json.loads(request.body) or {}
            update_data = data.get('update_data', None)
            if post == 'p' and update_data:
                id = data.get('post_id', None)
                post = PostSerializer(data=update_data, partial=True)
                if post.is_valid():
                    post.save(post_id)

            elif post == 'c' and update_data:
                id = data.get('comment_id', None)
                post = CommentSerializer(data=update_data, partial=True)
            elif post == 'r' and update_data:
                id = data.get('reply_id', None)
                post = ReplySerializer(data=update_data, partial=True)
            else:
                return Response({'message': 'proper key words missing.'}, status=401)
            
            if post.is_valid():
                post.save(id)
            
            return Response({'message': 'comment successfully updated'}, status=status.HTTP_200_OK)
        
    
    def delete(self, request, post, *args, **kwargs):
        pass
