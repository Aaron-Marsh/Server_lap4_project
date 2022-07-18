from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_users, name='get_users'),
    path('users/<str:username>', views.get_by_username, name='get_by_username'),
    path('users/register/', views.register, name='register'),
    path('users/login/', views.login, name='login'),

    # path('login', views.user_login),
    # path('logout', views.user_logout),
    # path('register', views.new_user)

    ]
