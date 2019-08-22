from rest_framework.viewsets import ModelViewSet
from timetracker.models import Employee
from timetracker.models import Checking
from timetracker.models import Vacation
from .serializers import EmployeeSerializer
from .serializers import CheckingSerializer
from .serializers import VacationSerializer


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class CheckingViewSet(ModelViewSet):
    queryset = Checking.objects.all()
    serializer_class = CheckingSerializer


class VacationViewSet(ModelViewSet):
    queryset = Vacation.objects.all()
    serializer_class = VacationSerializer
