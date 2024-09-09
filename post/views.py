from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from post.models import Post
from django.views import View
from datetime import datetime
from .serializers import PostSerializer
from django.http import JsonResponse
import json
# Create your views here.

class News(View):

    def get(self, request, index, *args, **kwargs):

            if index:
                user = User.objects.filter(username='emilyjim1').first()
                subscriptions = user.subscriptions.all()
                posts_from_subs = Post.objects.filter(user__in=subscriptions).order_by('-timestamp')
                paginator = Paginator(posts_from_subs, 20)
                paginated = paginator.get_page(index)
                pages = paginated.object_list

                serializer = PostSerializer(pages, has_next=paginated.has_next(), many=True)

       
            #if serializer.is_valid():
                return JsonResponse({'data': serializer.data }, status=200, safe=True)
            return JsonResponse({'data': None, 'message': 'no index provided'},
                        status=400, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class PostView(View):

    def get(self, request, *args, **kwargs):

        post_id = kwargs.get('id', None)
        if (not id or not isinstance(id, (int, str))) or \
                (not isinstance(page, int)):
                error = "kw arguement error: check page or id."
                return JsonResponse(data={'data': None,
                    'message': error}, status=400)

        if 'post' in request.url:
            comments = Post.objects.filter(pk=id).replies_to
            view_name  = 'post'
        elif 'comment' in request.url:
            comments = Comment.objects.filter(pk=id).replies_to
            view_name = 'comment'

        paginator = Paginator(comments, 30)
        paginated = paginator.get_page(page)
        comments = paginated.object_list
        has_next = paginated.has_next()

        url = {'id': id, 'view_name': view_name, 'page': page + 1}
        serialized_comments = PostSerializer(comments, fields=['id', 'comments', 'likes', 'views', 'text', 'user'], extra_kwargs={'url': url, 'next': has_next}, many=True)

        if serialized_comments.is_valid():
            return JsonResponse(data=serialized_comments.data, safe=True)
        return JsonResponse(data=serialized_comments.error, status=501)

    def post(self, request, post, *args, **kwargs):

        if post == 'p':
            try:
                user = User.objects.filter(pk=1125).first()
                data = json.loads(request.body) or {}
                text = data.get('post_data', {}).get('text', None)
                #img = request.FILES['image_file']
                #tagged_product = post_data.get('product', None)
                if not (text): # and  tagged_product):
                    return JsonResponse(data={'data': None,
                            'message': 'post should have a text message and a tagged product.'}, status=400)
                
                post = Post.objects.create(user=user, text=text)
            except json.JSONDecodeError as e:
                return JsonResponse(data={'data': None,
                    'message': 'data could not be parsed'}, status=501)
            return JsonResponse(data={'data': post.id, 'message':
                'post succefully added'}, status=200)
        
        elif post == 'c':
            post_id = kwargs.get('post_id', None)
            user = User.objects.filter(username='emilyjim1').first()
            post = Post.objects.filter(id=post_id).first()
            try:
                comment_data = json.loads(request.body)
                text = comment_data.get('text', None)
                comment = {'post': post, 'text': text, 'user': user}
                if text:
                    comment = Comment.objects.create(**comment)
                else:
                    return JsonResponse(data={'data': None, message: 'proper key words missing.'}, status=401)
            except json.JsonDECODERROR as e:
                return JsonRespone(data={'data': None, 'message': 'json decode error'}, status=501)
            return JsonResponse(data={'data': comment.id, 'message':
                    'comment succefully added'}, status=200)
