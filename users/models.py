""" from django.db import models


class Login(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=20)
    class Meta:
        db_table="Login"
 """