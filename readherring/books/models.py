from django.db import models
from django.forms import forms

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    ISBN = models.CharField(max_length=200, default='isbn')
    reviews = []
    rating = models.IntegerField(default=0)
    num_ratings = models.IntegerField(default=0)

    def __str__(self):
        return self.title

