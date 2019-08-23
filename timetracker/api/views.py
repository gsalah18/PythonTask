import json
from datetime import timedelta
from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from timetracker.models import Employee
from timetracker.models import Checking
from .serializers import EmployeeSerializer
from .serializers import CheckingSerializer
from .serializers import VacationSerializer


class EmployeeViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    YEAR_QUARTERS = {
        '1': [1, 3],
        '2': [3, 6],
        '3': [6, 9],
        '4': [9, 12]
    }

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated],
            url_path='set-check', url_name='set_check')
    def set_checking(self, request, pk=None):
        check = request.data['check'] if 'check' in request.data else ''
        checking_serializer = CheckingSerializer(data={'check': check, 'employee': pk})
        if checking_serializer.is_valid():
            checking_serializer.save()
            return Response({'result': checking_serializer.data, 'error': None}, status=status.HTTP_201_CREATED)
        return Response({'error': json.dumps(checking_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated],
            url_path='set-vacation', url_name='set_vacation')
    def set_vacation(self, request, pk=None):
        vacation_serializer = VacationSerializer(
            data={'employee': pk,
                  'description': request.data['description'] if 'description' in request.data else ''})
        if vacation_serializer.is_valid():
            vacation_serializer.save()
            return Response({'result': vacation_serializer.data, 'error': None}, status=status.HTTP_201_CREATED)
        return Response({'error': json.dumps(vacation_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=True, permission_classes=[IsAuthenticated],
            url_path='work-avg', url_name='work_avg')
    def get_work_avg(self, request, pk=None):
        try:
            employee = Employee.objects.get(id=pk)
        except:
            employee = None
        if employee is None:
            return Response({'error': 'Employee is not found for id {}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        check_in_count = employee.checking_set.filter(check='in').count()
        check_out_count = employee.checking_set.filter(check='out').count()
        average = (check_in_count + check_out_count) / 2
        return Response({'result': average, 'error': None}, status=status.HTTP_200_OK)

    '''

        1- Working hours are the checkim times 8 assuming 8 is a day working hours.
        2- period value pattern is pipe seperated:
            a.for the quarter would be the year piped by the quarter, ex: 2019|1 (Year 2019 the first quarter)
            b.for the week would be the date(year/month/day) which will represent the first day of the week
    '''

    @action(methods=['GET'], detail=True, permission_classes=[IsAuthenticated],
            url_path='work-hours', url_name='work_avg')
    def get_work_hour_in_period(self, request, pk=None):
        try:
            employee = Employee.objects.get(id=pk)
        except:
            employee = None
        if employee is None:
            return Response({'error': 'Employee is not found for id {}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        period_value = request.query_params['period_value'] if 'period_value' in request.query_params else None
        period_type = request.query_params['period_type'] if 'period_type' in request.query_params else None
        if period_value is None or period_type is None:
            return Response({'error': 'Either period_value or period_value type is missing'},
                            status=status.HTTP_400_BAD_REQUEST)

        if period_type == 'year':
            if not (self.is_a_number(period_value)):
                Response({'error': 'period value is invalid, year input should be only digits, ex:2019'},
                         status=status.HTTP_400_BAD_REQUEST)
            emp_checkins = employee.checking_set.all().filter(check='in', time__year=period_value).count()

        elif period_type == 'quarter':
            if len(period_value.split('|')) != 2:
                Response(
                    {'error': 'period value is invalid, quarter input should be year piped by quarter, ex: 2019|3'},
                    status=status.HTTP_400_BAD_REQUEST)
            year = period_value.split('|')[0]
            quarter = period_value.split('|')[1]
            if not (self.is_a_number(year)) or not (self.is_a_number(quarter)) or not (1 <= int(quarter) <= 4):
                Response(
                    {'error': 'period value is invalid, quarter input should be year piped by quarter, ex: 2019|3'},
                    status=status.HTTP_400_BAD_REQUEST)
            emp_checkins = employee.checking_set.all().filter(check='in',
                                                              time__range=['{}-{}-01'.format(year, self.YEAR_QUARTERS[
                                                                  quarter][0]),
                                                                           '{}-{}-01'.format(year,
                                                                                             self.YEAR_QUARTERS[
                                                                                                 quarter][
                                                                                                 1])]).count()

        elif period_type == 'week':
            try:
                date_value = datetime.strptime(period_value, '%Y-%m-%d')
            except ValueError:
                Response({'error': 'period value is invalid, week input should be date dash seperated, ex: 2019-3-18'},
                         status=status.HTTP_400_BAD_REQUEST)
            emp_checkins = employee.checking_set.all().filter(check='in',
                                                              time__range=[date_value,
                                                                           date_value + timedelta(weeks=1)]).count()

        else:
            emp_checkins = None
        if emp_checkins is None:
            return Response({'error': 'prod type is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'result': emp_checkins * 8, 'error': None}, status=status.HTTP_200_OK)

    def is_a_number(self, str):
        return any(char.isdigit() for char in str)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_team_work_percent(request):
    team_checkins = Checking.objects.filter(check='in').count()
    team_checkouts = Checking.objects.filter(check='out').count()
    team_work_percent = team_checkins / team_checkouts * 100
    return Response({'result': '{}%'.format(team_work_percent)}, status=status.HTTP_200_OK)
