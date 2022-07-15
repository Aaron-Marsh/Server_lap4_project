from django.urls import path
from . import views

urlpatterns = [
    path('forums/', views.get_create_threads, name='get_create_threads'),
    path('forums/<int:ISBN>', views.get_by_ISBN, name='get_by_ISBN'),
    ]
