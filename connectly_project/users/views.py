from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.shortcuts import render
import pyrebase
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

config = {
    "apiKey": os.getenv('FIREBASE_API_KEY'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
    "projectId": os.getenv('FIREBASE_PROJECT_ID'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    "appId": os.getenv('FIREBASE_APP_ID')
}

firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()


# Create your views here.
# @csrf_exempt
# def get_users(request):
#     if request.method == 'GET':
#         try:
#             users = User.objects.all()
#             return JsonResponse({'users': list(users.values())}, safe=False, status=200)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, safe=False, status=400)


# # Get user by id
# @csrf_exempt
# def get_user_by_id(request, id):
#     if request.method == 'GET':
#         try:
#             user = User.objects.get(id=id)
#             return JsonResponse({'id': user.id, 'username': user.username, 'email': user.email, 'created_at': user.created_at}, safe=False, status=200)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, safe=False, status=400)


# # Create a new user
# @csrf_exempt
# def create_user(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             user = User.objects.create(username=data['username'], email=data['email'])
#             return JsonResponse({'message': 'User created successfully', 'user': user.username}, safe=False, status=201)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, safe=False, status=400)


# # Update a user
# @csrf_exempt
# def update_user(request, id):
#     if request.method == 'PUT':
#         try:
#             data = json.loads(request.body)
#             user = User.objects.get(id=id)
#             user.username = data['username']
#             user.email = data['email']
#             user.save()
#             return JsonResponse({'message': 'User updated successfully', 'user': user.username}, safe=False, status=200)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, safe=False, status=400)


# # Delete a user
# @csrf_exempt
# def delete_user(request, id):
#     if request.method == 'DELETE':
#         try:
#             user = User.objects.get(id=id)
#             user.delete()
#             return JsonResponse({'message': 'User deleted successfully'}, safe=False, status=204)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, safe=False, status=400)
    

# Firebase
@csrf_exempt
def home(request, username=None):
    if request.method == 'GET':
        try:
            # Get all users
            users = database.child('users').get()
            # Find user with matching username
            user_data = None
            if users.each():
                for user in users.each():
                    if user.val() and user.val().get('username') == username:
                        user_data = user.val()
                        break
            
            if user_data:
                return render(request, "users/user.html", {
                    "username": user_data.get('username'),
                    "email": user_data.get('email')
                })
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def get_users(request):
    if request.method == 'GET':
        try:
            users = database.child('users').get()
            # Filter out None values and create a clean list
            users_list = [
                {'id': user.key(), **user.val()} 
                for user in users.each() 
                if user.val() is not None
            ] if users.each() else []
            return JsonResponse({'users': users_list}, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)

@csrf_exempt
def get_user_by_id(request, id):
    if request.method == 'GET':
        try:
            user = database.child('users').child(id).get().val()
            if user:
                return JsonResponse(user, safe=False, status=200)
            return JsonResponse({'error': 'User not found'}, safe=False, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_data = {
                'username': data['username'],
                'email': data['email']
            }
            result = database.child('users').push(user_data)
            user_id = result['name']
            
            return JsonResponse({
                'message': 'User created successfully',
                'user_id': user_id,
                'user': user_data
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)

@csrf_exempt
def update_user(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user = database.child('users').child(str(id)).get().val()
            if not user:
                return JsonResponse({'error': 'User not found'}, safe=False, status=404)
            
            user_data = {
                'username': data.get('username', user.get('username')),
                'email': data.get('email', user.get('email'))
            }
            database.child('users').child(str(id)).update(user_data)
            return JsonResponse({
                'message': 'User updated successfully',
                'user': user_data
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)

@csrf_exempt
def delete_user(request, id):
    if request.method == 'DELETE':
        try:
            user = database.child('users').child(str(id)).get().val()
            if not user:
                return JsonResponse({'error': 'User not found'}, safe=False, status=404)
            
            database.child('users').child(str(id)).remove()
            return JsonResponse({'message': 'User deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=400)