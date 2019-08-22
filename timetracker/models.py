from django.db import models
from django.utils import timezone


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    dateadded = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username


class Vacation(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
