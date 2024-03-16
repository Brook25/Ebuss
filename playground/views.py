from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from .serializers import PostSerializer, PostWithLinkSerializer
# Create your views here.

class Posts(View):

    def get(self, request, *args, **kwargs):
        new_posts = [ 
            {
                'id': '1111',
                'name': 'John',
                'prof_pic': 'J',
                'content': 'New product is out',
                'image': None,
                'comments': 20,
                'likes': 30,
                'shares': 8,
                'posted_at': '2023/8/10'
            },
            {
                'id': '2222',
                'name': 'Peter',
                'prof_pic': 'P',
                'content': 'Check out our new T-shirts',
                'image': None,
                'comments': 25,
                'likes': 40,
                'shares': 9,
                'posted_at': '2023/9/20'
            }
        ]

        more_link = 'posts'  + 'John' + '1'

        posts = PostWithLinkSerializer(data={'new_posts': new_posts, 'more_link': more_link})

        if posts.is_valid():
            posts_data = posts.data
            print('hello', posts_data)
            return JsonResponse(posts_data)

        else:
            print('hello:error')
            return JsonResponse(posts.errors)
