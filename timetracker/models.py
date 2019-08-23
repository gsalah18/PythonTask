from django.db import models
from django.utils import timezone
from datetime import date


# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name


class Checking(models.Model):
    checkChoices = [
        ('in', 'Check-in'),
        ('out', 'Check-out')
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    check = models.CharField(max_length=3, choices=checkChoices, blank=False)
    time = models.DateTimeField(default=timezone.now)


class Vacation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=False)
    description = models.TextField(default='', blank=True)
    date = models.DateField(default=date.today())
