from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_create_threads, name='get_create_threads'),
    path('users/<str:id>', views.get_by_id, name='get_by_id'),
    ]
