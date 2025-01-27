from django.urls import path
from .views import PostListCreate, CommentListCreate


urlpatterns = [
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
]

