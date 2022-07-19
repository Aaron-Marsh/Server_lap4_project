from django.db import models
from django.forms import forms

class Thread(models.Model):
    title = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    first_message = models.CharField(max_length=1000)
    replies = []

    def __str__(self):
        return self.title

