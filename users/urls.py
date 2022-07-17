from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_users, name='get_users'),
    path('users/<str:username>', views.get_by_username, name='get_by_username'),
    ]
