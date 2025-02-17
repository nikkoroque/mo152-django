from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer


# Create your views here.
@csrf_exempt
def get_users(request):
    if request.method == 'GET':
        try:
            users = User.objects.all()
            return JsonResponse({'users': list(users.values())}, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)


# Get user by id
@csrf_exempt
def get_user_by_id(request, id):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=id)
            return JsonResponse({'id': user.id, 'username': user.username, 'email': user.email, 'created_at': user.created_at}, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)


# Create a new user
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Update a user
@csrf_exempt
def update_user(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=id)
            user.username = data['username']
            user.email = data['email']
            user.save()
            return JsonResponse({'message': 'User updated successfully', 'user': user.username}, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)


# Delete a user
@csrf_exempt
def delete_user(request, id):
    if request.method == 'DELETE':
        try:
            user = User.objects.get(id=id)
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'}, safe=False, status=204)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)


# User view
def user_view(request):
    return render(request, 'users/user.html')

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    