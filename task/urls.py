from django.contrib import admin
from django.urls import path, include
from rest_framework import status
from rest_framework.response import Response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('timetracker/', include('timetracker.urls'))
]
