from django.db import models
from django.utils import timezone


# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Checking(models.Model):
    checkChoices = [
        ('in', 'Check-in'),
        ('out', 'Check-out')
    ]
    userid = models.ForeignKey(Employee, on_delete=models.CASCADE)
    check = models.CharField(max_length=3, choices=checkChoices)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.userid, self.check, self.time

class Vacation(models.Model):
    userid = models.ForeignKey(Employee, on_delete=models.CASCADE)
    description = models.TextField(default='')
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.userid, self.description, self.date
