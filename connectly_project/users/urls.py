from django.urls import path
from . import views
from .views import get_auth_token

urlpatterns = [
    path('user-list/', views.get_users, name='get_users'),
    path('create/', views.create_user, name='create_user'),
    path('update/<int:id>/', views.update_user, name='update_user'),
    path('delete/<int:id>/', views.delete_user, name='delete_user'),
    path('get-user/<int:id>/', views.get_user_by_id, name='get_user_by_id'),
    path('user-page/', views.user_view, name='user_view'),
    path('login/', views.login_user, name='login_user'),
    path('auth/token/', get_auth_token, name='get-auth-token'),
]
