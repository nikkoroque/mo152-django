from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsPostAuthor


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


class PostListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None

    def check_object_permissions(self, request, obj):
        # First check if user is admin
        if request.user.groups.filter(name='Admin').exists():
            return True
            
        # If not admin, check if user is the author
        if obj.author != request.user:
            self.permission_denied(
                request,
                message='You do not have permission to perform this action.',
            )
        return True

    def get(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Check if user is admin
        if not request.user.groups.filter(name='Admin').exists():
            # If not admin, check if user is the author
            if post.author != request.user:
                return Response(
                    {'error': 'You do not have permission to perform this action.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
