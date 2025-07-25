"""
URL configuration for appstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('user/', include('user.urls')),
    path('news/', include('post.news_urls')),
    path('timeline/', include('post.timeline_url')),
    path('post/', include('post.urls')),
    path('product/', include('product.urls')),
    path('cart/', include('cart.urls')),
    path('popular/', include('product.popular_urls')),
    path('order/', include('order.urls')),
    path('payment-webhook/', include('order.webhook_urls')),
    path('subcategory/', include('product.subcat_urls')),
    path('category/', include('product.cat_urls')),
    path('dashboard/', include('supplier.urls')),
    path('auth/', include('Auth.urls'))
]
