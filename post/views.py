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
                user = User.objects.filter(username='emilyjim1').first()
                subscriptions = user.subscriptions.all()
                all_posts = Post.objects.filter(Q(user__in=subscriptions) | Q(user=user)).order_by('-timestamp')
                posts = paginate_queryset(posts_from_subs, request, PostSerializer, index=index)

                return Response({'message': f'news page index {index} successfully retreived' }, status=200)
            return Response({'message': 'no index provided'},
                        status=400)


class Timeline(View):

    def get(self, request, index, *args, **kwargs):
        user = User.objects.filter(username='emilyjim1').first()
        my_posts = user.posts.all().order_by('-timestamp')
        posts = paginate_queryset(posts_from_subs, request, PostSerializer, index=index)

        return Response({'message': 'data successfully retreived' status=200)


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
        elif post == 'c':
            comments = Comment.objects.filter(pk=id).first().replies_to.all()
        else:
            comments = Reply.object.filter(pk=id).first().replies_to.all()
        
        comments = paginate_queryset(comments, request, CommentSerializer)


        return Response({ 'message': 'data successfully retreived', 
            }, status=200)

    def post(self, request, post, *args, **kwargs):

        if post == 'p':
            try:
                user = User.objects.filter(pk=1125).first()
                data = json.loads(request.body) or {}
                text = data.get('post_data', {}).get('text', '')
                img = request.FILES['image_file'] or None
                #tagged_product = post_data.get('product', None)
                if not (text): # and  tagged_product):
                    return Response({
                            'message': 'post should have a text message and a tagged product.'}, status=400)
                post = PostSerializer(data={'user': user, 'text': text, 'img': img})
                if post.is_valid():
                    post.create(data)
                return JsonResponse(data={'data': post.id, 'message':
                    'post succefully added'}, status=200)
            except json.JSONDecodeError as e:
                return JsonResponse(data={'data': None,
                    'message': 'data could not be parsed'}, status=501)
        
        elif post == 'c':
            data = json.loads(request.body) or {}
            post_id = data.get('post_id', None)
            comment_id = data.get('comment_id', None)
            user = User.objects.filter(username='emilyjim1').first()
            text = data.get('text', '')
            if post_id and text:
                post = Post.objects.filter(pk=post_id).first()
                reply_data = {'post': post, 'text': text, 'user': user}
                reply = CommentSerializer(data=reply)
            elif comment_id and text:
                comment = Comment.objects.filter(pk=comment_id).first()
                reply_data = {'comment': comment, 'text': text, 'user': user}
                reply = ReplySerializer(data=reply_data)
            else:
                return Response({'message': 'proper key words missing.'}, status=401)
            if reply.is_valid():
                reply.create(reply_data)
            return Response({'data': comment.id,
                    'message': 'comment successfully added'},
                        status=200)

    def put(self, request, post, *args, **kwargs):
        pass
    
    def delete(self, request, post, *args, **kwargs):
        pass
