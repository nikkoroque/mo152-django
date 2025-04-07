from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .permissions import IsPostAuthor, CanViewPost
from django.db import models
from rest_framework.generics import ListAPIView
from django.core.cache import cache
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination




# class UserListCreate(APIView):
#     def get(self, request):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)


#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Default posts per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get public posts or posts authored by the user
        posts = Post.objects.filter(
            models.Q(privacy='public') |
            models.Q(author=request.user)
        )

        # Admin users can see all posts
        if request.user.groups.filter(name='Admin').exists():
            posts = Post.objects.all()

        # Apply pagination
        paginator = StandardResultsSetPagination()
        paginated_posts = paginator.paginate_queryset(posts.order_by('-created_at'), request)
        serializer = PostSerializer(paginated_posts, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['author'] = request.user.id
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        data = request.data.copy()
        data['author'] = request.user.id
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, CanViewPost]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        # Only admin users or post authors can delete posts
        if request.user.groups.filter(name='Admin').exists() or post.author == request.user:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """Like a post."""
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            return Response({"message": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Post liked successfully"}, status=status.HTTP_201_CREATED)
    
class UnlikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        """Unlike a post."""
        post = get_object_or_404(Post, id=post_id)
        like = Like.objects.filter(user=request.user, post=post)

        if not like.exists():
            return Response({"message": "You haven't liked this post yet."}, status=status.HTTP_400_BAD_REQUEST)

        like.delete()
        return Response({"message": "Post unliked successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class FeedView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Show public posts to everyone, and private posts only to the owner
        posts = Post.objects.filter(
            Q(privacy="public") | Q(privacy="private", author=user)
        ).order_by("-created_at")

        # Optional: Get posts liked by the user
        liked_posts = self.request.query_params.get("liked", None)
        if liked_posts == "true":
            posts = posts.filter(likes__user=user)

        # Prefetch related data for performance
        posts = posts.prefetch_related("comments", "likes")

        # Caching frequently accessed posts
        cache_key = f"user_feed_{user.id}"
        cached_posts = cache.get(cache_key)
        if cached_posts:
            return cached_posts

        cache.set(cache_key, posts, timeout=60 * 5)  # Cache for 5 minutes
        return posts
