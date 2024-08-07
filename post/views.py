from django.shortcuts import render
from django.core import Paginator
from user.models import User
from post.models import Post
from django.views import View
from datetime import datetime
from seriazlizers import PostSerializer
from django.http import JsonResponse
# Create your views here.

class News(View):

    def get(self, request, *args, **kwargs):

            page = kwargs.get('page', 0)
            if page:
                paginate = Paginator()
                posts_from_subs = request.user.subscriptions.posts.all()
                posts_from_subs = posts_from_subs.filter(timestamp__lte=datetime.now())
                paginator = Paginator(posts_from_subs, 20)
                paginated = paginator.get_page(page)
                pages = paginated.object_list
                url = {'page': page + 1,  'view_name': 'news'}
                fields = ['id', 'comments', 'likes', 'views', 'image', 'text', 'user']

                serializer = PostSerializer(pages, model='Post', fields=fields, extra_kwargs={'url': url, 'has_next': paginated.has_next()}, many=True)

       
                if serializer.is_valid():
                    return JsonResponse(serializer.data, safe=True)
        return JsonResponse(serialzer.error, status=501, safe=True)


class Post(View):

    def get(self, request, *args, **kwargs):

        pk, page = args
        if (not pk or not isinstance(id, (int, str))) or \
                (not page or not isinstance(page, int)):
                error = "Positional arguement error: check page or id."
                return JsonResponse(data={'data': None,
                    'message': error}, status=401)

        if 'post' in request.url:
            comments = Post.objects.filter(pk=id).replies_to
            view_name  = 'post'
        elif 'comment' in request.url:
            comments = Comment.objects.filter(id=id).replies_to
            view_name = 'comment'

        paginator = Paginator(comments, 50)
        paginated = paginator.get_page(page)
        comments = paginated.object_list
        has_next = paginated.has_next()

        url = {'id': id, 'view_name': view_name, 'page': page + 1}
        serialized_comments = PostSerializer(comments, fields=['id', 'comments', 'likes', 'views', 'text', 'user'], extra_kwargs={'url': url, 'next': has_next} many=True)

        if serialized_comments.is_valid():
            return JsonResponse(data=serialized_comments.data, safe=True)
        return JsonResponse(data=serialized_comments.error, status=501)

    def post(self, request, *args, **kwargs):

        if 'post' in request.url:
            try:
                post_data = json.loads(request.body)
                text = post_data.get('text', None)
                img = request.FILES['image_file']
                tagged_product = post_data.get('product', None)
                if not (text and  tagged_product):
                    return JsonResponse(data={'data': None,
                            'message': 'post should have a text message and a tagged product.'}, status=401)

            except JSONDecodeError as e:
                return JsonResponse(data={'data': None,
                    'message': 'data could not be parsed'}, status=501)
            return JsonResponse(data={'data': comment.id, 'message':
                'post succefully added'}, status=200)
        
        elif 'comment' in request.url and args[0] and type(args) is int:
                post_id = args[0]
                try:
                    comment_data = json.loads(request.body)
                    text = comment_data.get('text', None)
                    date = comment_data.get('date', None)
                    comment = {'post': post, 'text': text, 'date': date, 'user': request.user}
                    if text and date and comment_by:
                        comment = Comment.objects.create(**comment)
                    else:
                        return JsonResponse(data={'data': None, message: 'proper key words missing.'}, status=401)
                except JsonDECODERROR as e:
                    return JsonRespone(data={'data': None, 'message': 'json decode error'}, status=501)
                return JsonResponse(data={'data': comment.id, 'message':
                    'comment succefully added'}, status=200)
