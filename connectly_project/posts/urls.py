from django.urls import path
from .views import PostListCreate, PostDetailView, LikePostView, UnlikePostView, FeedView


urlpatterns = [
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like-post'),  # Like a post
    path('posts/<int:post_id>/unlike/', UnlikePostView.as_view(), name='unlike-post'),  # Unlike a post
    path("feed/", FeedView.as_view(), name="feed"),
]

