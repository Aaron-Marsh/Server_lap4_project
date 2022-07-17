from django.db import models

# Create your models here.
from django.db import models

class Login(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=10)
    class Meta:
        db_table="Login"
