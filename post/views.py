from django.shortcuts import get_object_or_404
from django.db.models import (F, Q)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from .models import (Post, Comment)
from .serializers import (PostSerializer, CommentSerializer)
from django.views import View
from datetime import datetime
from .serializers import PostSerializer
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import json
from shared.utils import paginate_queryset
# Create your views here.

class News(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):

            if index:
                subscriptions = request.user.subscriptions.all()
                all_posts = Post.objects.filter(Q(user__in=subscriptions) | Q(user=request.user)).order_by('-created_at')
                posts = paginate_queryset(all_posts, request, PostSerializer)

                return Response(posts.data, status=status.HTTP_200_OK)
            return Response({'message': 'no index provided'},
                        status=status.HTTP_400_BAD_REQUEST)


class Timeline(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):
        my_posts = Post.objects.filter(user=request.user).order_by('-created_at')
        posts = paginate_queryset(my_posts, request, PostSerializer)

        return Response(posts.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class PostView(APIView):
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
        obj = get_object_or_404(model, pk=id)
        serializer = self.POST_MODELS.get(post, {}).get('serializer', None)
        comments = obj.replies_to.all().select_related('user')
        
        comments = paginate_queryset(comments, request, serializer)

        return Response(comments.data, status=status.HTTP_200_OK)

    def post(self, request, post, *args, **kwargs):

        model = self.POST_MODELS.get(post, {}).get('model', Comment)
        serializer = self.POST_MODELS.get(post, {}).get('serializer', CommentSerializer)
        data = request.data
        text = data.get('text', '')
        obj_data = {'user': request.user.pk, 'text': text}
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
            parent_name = 'post' if post == 'p' else 'parent_comment'
            parent_id = data.get('parent_id', None)
            obj_data[parent_name] = parent_id
        obj = serializer(data=obj_data)
        
        if obj.is_valid():
            obj.create()
            
            return Response(data={'message':
                '{} successfully added'.format(model.__name__)}, status=status.HTTP_200_OK)
        
        return Response(obj.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post, index, *args, **kwargs):
        if not isinstance(index, int):
            return Response({'message': 'index should be integer'}, status=status.HTTP_400_BAD_REQUEST)
        model = self.POST_MODELS.get(post, {}).get('model', None)
        if model:
            posted_obj = get_object_or_404(model, pk=index)
            if model == 'c':
                if posted_obj.parent_comment:
                    posted_obj.parent_comment.comments = F('comments') - 1
                    posted_obj.parent_comment.save()
                else:
                    posted_obj.post.comments = F('comments') - 1
                    posted_obj.post.save()
            posted_obj.delete()
            return Response({'message': '{} succefully deleted'.format(model.__name__)}, status=status.HTTP_200_OK)


class LikeView(APIView):

    def post(self, request, post, path,  pk, *args, **kwargs):

        Model = Post if post == 'p' else Comment
        obj = get_object_or_404(Model, pk=pk)
        amount = request.data.get('amount', 0)

        if path == 'like':
            obj.likes = F('likes') + amount
            obj.save(update_fields=['likes'])
        elif path == 'view':
            obj.views = F('views') + amount
            obj.save(update_fields=['views'])
        else:
            return Response({'message': 'wrong parameter'}, status=status.HTTP_400_BAD_REQUEST)
        
        obj.save()
        return Response({'message: amount succefully added.'}, status=status.HTTP_200_OK)
