from django.urls import path
from . import views

urlpatterns = [
    path('user-list/', views.get_users, name='get_users'),
    path('create/', views.create_user, name='create_user'),
    path('update/<str:id>/', views.update_user, name='update_user'),
    path('delete/<str:id>/', views.delete_user, name='delete_user'),
    path('get-user/<str:id>/', views.get_user_by_id, name='get_user_by_id'),
    path('user/<str:username>/', views.home, name='home'),
]