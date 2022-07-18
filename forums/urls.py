from django.urls import path
from . import views

urlpatterns = [
    path('forums/', views.get_threads, name='get_create_threads'),
    path('forums/<str:id>', views.get_by_id, name='get_by_id'),
    path('forums/search/', views.search_by_title, name='search_by_title'),
    ]
