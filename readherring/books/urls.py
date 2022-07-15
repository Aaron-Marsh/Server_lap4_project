from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.get_all_books, name='get_all_books'),
    path('books/<int:ISBN>', views.get_by_ISBN, name='get_by_ISBN'),
    ]
