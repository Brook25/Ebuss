from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from .models import (Post, Comment)
from .serializers import (PostSerializer, CommentSerializer)
from django.views import View
from datetime import datetime
from .signals import increment_no_comments
from .serializers import PostSerializer
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework import status
import json
from shared.utils import paginate_queryset
# Create your views here.

class News(View):
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):

            if index:
                subscriptions = request.user.subscriptions.all()
                all_posts = Post.objects.filter(Q(user__in=subscriptions) | Q(user=request.user)).order_by('-created_at')
                posts = paginate_queryset(all_posts, request, PostSerializer)

                return Response(posts, status=status.HTTP_200_OK)
            return Response({'message': 'no index provided'},
                        status=status.HTTP_400_BAD_REQUEST)


class Timeline(View):
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):
        my_posts = request.user.posts.all().order_by('-created_at')
        posts = paginate_queryset(my_posts, request, PostSerializer)

        return Response(posts, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class PostView(View):
    permission_classes = [IsAuthenticated]

    POST_MODELS = {'p': {'model': Post, 'serializer': PostSerializer},
                        'c':{'model': Comment, 'serializer': CommentSerializer},
                            }

    def get(self, request, post, *args, **kwargs):

        id = self.request.GET.get('id', None)
        page = self.request.GET.get('page', 0)
        if not (id and page.isdigit()):
            error = "kw arguement error: check page or id."
            return Response(
                {'message': error}, status=status.HTTP_400_BAD_REQUEST)

        model = self.POST_MODELS.get(post, {}).get('model', None)
        serializer = self.POST_MODELS.get(post, {}).get('serializer', None)
        comments = model.objects.get(pk=id).replies_to.all()
        
        comments = paginate_queryset(comments, request, serializer)

        return Response(comments, status=status.HTTP_200_OK)

    def post(self, request, post, *args, **kwargs):

        model = self.POST_MODELS.get(post, {}).get('model', Comment)
        serializer = self.POST_MODELS.get(post, {}).get('serializer', CommentSerializer)
        data = request.data
        text = data.get('text', '')
        obj_data = {'user': request.user, 'text': text}
        if not text:
            return Response({
                    'message': 'post should have a text message and a tagged product.'},
                      status=status.HTTP_400_BAD_REQUEST)
        if post == 'p':
            img = request.FILES['image_file']
            tagged_product = data.get('product', None)
            obj_data['image'] = img
            obj_data['tagged_product'] = tagged_product
        else:
            parent_name = 'post' if post == 'p' else 'comment'
            parent_id = data.get('parent_id', None)
            parent = get_object_or_404(model, pk=parent_id)
            obj_data[parent_name] = parent
        obj = serializer(data=obj_data)
        
        if obj.is_valid():
            obj.create()
        
        return Response(data={'message':
            '{} successfully added'.format(model.__name__)}, status=status.HTTP_200_OK)
        

    def delete(self, request, post, index, *args, **kwargs):
        if not index.is_digit():
            return Response({'message': 'index should be integer'}, status=status.HTTP_400_BAD_REQUEST)
        model = self.POST_MODELS.get(post, {}).get('model', None)
        if model:
            post = get_object_or_404(model, pk=index)
            post.delete()
            return Response({'message': '{} succefully deleted'.format(model.__name__)}, status=HTTP_400_OK)
