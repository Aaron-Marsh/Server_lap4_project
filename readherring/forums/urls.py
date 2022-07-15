from django.urls import path
from . import views

urlpatterns = [
    path('forums/', views.get_create_threads, name='get_create_threads'),
    path('forums/<str:id>', views.get_by_id, name='get_by_id'),
    ]
