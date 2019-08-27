from django.db import models


# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name


class Checking(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    checkin = models.FloatField(blank=False)
    checkout = models.FloatField(blank=True, null=True, default=None)

    def __str__(self):
        return self.employee.name

class Vacation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=False)
    description = models.TextField(default='', blank=True)
    date = models.DateField(blank=False)

    def __str__(self):
        return self.employee.name, self.description
