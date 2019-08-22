# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework import status

from rest_framework.viewsets import ModelViewSet
from timetracker.models import User
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
