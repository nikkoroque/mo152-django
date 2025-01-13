from django.shortcuts import render
from django.http import JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json

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
@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create(username=data['username'], email=data['email'])
            return JsonResponse({'message': 'User created successfully', 'user': user.username}, safe=False, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)


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
