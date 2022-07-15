from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    ISBN = models.CharField(max_length=200, default='isbn')

    def __str__(self):
        return self.title

