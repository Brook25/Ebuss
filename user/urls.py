from django.urls import path
from .views import (HistoryView, NotificationView,
        Recent, WishListView, Subscriptions)


urlpatterns = [
    path('notif/<int:index>/', NotificationView.as_view(), name='notif'),
    path('history/<int:index>/', HistoryView.as_view(), name='history'),
    path('wishlist/', WishListView.as_view(), name='wishlist'),
    path('recent/', Recent.as_view(), name='recent'),
    path('subs/<int:index>', Subscriptions.as_view(), name='subscription')
]
