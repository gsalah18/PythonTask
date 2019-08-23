from django.contrib import admin
from .models import Employee
from .models import Checking
from .models import WorkingHours
from .models import Vacation
# Register your models here.

admin.site.register(Employee)
admin.site.register(Checking)
admin.site.register(WorkingHours)
admin.site.register(Vacation)