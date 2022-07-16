from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.get_create_books, name='get_create_books'),
    path('books/<int:ISBN>', views.get_by_ISBN, name='get_by_ISBN'),
    path('books/api/', views.get_books_from_api, name='get_books_from_api'),
    ]
