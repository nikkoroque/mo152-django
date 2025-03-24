from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class CanViewPost(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin users can view all posts
        if request.user.groups.filter(name='Admin').exists():
            return True
        # Author can view their own posts
        if obj.author == request.user:
            return True
        # Public posts can be viewed by anyone
        if obj.privacy == 'public':
            return True
        return False 