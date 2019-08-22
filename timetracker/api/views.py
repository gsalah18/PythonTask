from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from timetracker.models import Employee
from timetracker.models import Checking
from timetracker.models import Vacation
from .serializers import EmployeeSerializer
from .serializers import CheckingSerializer
from .serializers import VacationSerializer


class EmployeeViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated],
            url_path='set-check', url_name='set_check')
    def set_checking(self, request, pk=None):
        check = request.data['check'] if 'check' in request.data else ''
        checking_serializer = CheckingSerializer(data={'check': check, 'employee': pk})
        if checking_serializer.is_valid():
            checking_serializer.save()
            return Response(checking_serializer.data, status=status.HTTP_201_CREATED)
        return Response(checking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated],
            url_path='set-vacation', url_name='set_vacation')
    def set_vacation(self, request, pk=None):
        vacation_serializer = VacationSerializer(
            data={'employee': pk,
                  'description': request.data['description'] if 'description' in request.data else ''})
        if vacation_serializer.is_valid():
            vacation_serializer.save()
            return Response(vacation_serializer.data, status=status.HTTP_201_CREATED)
        return Response(vacation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Checking.objects.all()
    serializer_class = CheckingSerializer


class VacationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Vacation.objects.all()
    serializer_class = VacationSerializer
