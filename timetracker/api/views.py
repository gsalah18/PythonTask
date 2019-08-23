import json
from datetime import timedelta
from datetime import datetime

from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from timetracker.models import Employee, WorkingHours
from timetracker.models import Checking
from .serializers import EmployeeSerializer, WorkingHoursSerializer
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
        time_now = datetime.now()
        checking_serializer = CheckingSerializer(data={'check': check, 'time': time_now, 'employee': pk})
        if checking_serializer.is_valid():
            checking_serializer.save()
            '''
            So ٍBasically here, whenever a checkout is entered then I'm assuming its end of a working day,
            so I calculated working our for that day.
            '''
            if check == 'out':
                try:
                    checkin_same_day = Employee.objects.get(id=pk).checking_set.all().filter(time__year=time_now.year,
                                                                                             time__month=time_now.month,
                                                                                             time__day=time_now.day)[0]
                    working_hours = int((checkin_same_day.time.replace(tzinfo=None) - time_now).seconds / 60 / 60)
                    working_hours_serializer = WorkingHoursSerializer(
                        data={'employee': pk, 'hours': working_hours, 'date': time_now})
                    if working_hours_serializer.is_valid():
                        working_hours_serializer.save()
                except Checking.DoesNotExist:
                    pass

            return Response({'result': checking_serializer.data, 'error': None}, status=status.HTTP_201_CREATED)
        return Response({'error': json.dumps(checking_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated],
            url_path='set-vacation', url_name='set_vacation')
    def set_vacation(self, request, pk=None):
        try:
            if ('date' in request.data):
                datetime.strptime(request.data['date'], '%Y-%m-%d')
        except ValueError:
            return Response({'error': 'Date is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        vacation_serializer = VacationSerializer(
            data={'employee': pk,
                  'description': request.data['description'] if 'description' in request.data else '',
                  'date': datetime.strptime(request.data['date'],'%Y-%m-%d').date()
                  if 'date' in request.data else None})
        if vacation_serializer.is_valid():
            vacation_serializer.save()
            return Response({'result': vacation_serializer.data, 'error': None}, status=status.HTTP_201_CREATED)
        return Response({'error': json.dumps(vacation_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=True, permission_classes=[IsAuthenticated],
            url_path='work-avg', url_name='work_avg')
    def get_work_avg(self, request, pk=None):
        try:
            employee = Employee.objects.get(id=pk)
        except Employee.DoesNotExist:
            employee = None
        if employee is None:
            return Response({'error': 'Employee is not found for id {}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        check_in_times = employee.checking_set.filter(check='in').values_list('time')
        check_out_times = employee.checking_set.filter(check='out').values_list('time')
        if (check_in_times.count() == 0 or check_out_times.count() == 0):
            return Response({'error': 'There is no checkout Data'}, status=status.HTTP_400_BAD_REQUEST)

        arrival_avg_time = self.get_dates_avg(check_in_times)
        leaving_avg_time = self.get_dates_avg(check_out_times)
        return Response({'result': {'arrival_time': '{}:{}'.format(arrival_avg_time.hour, arrival_avg_time.minute),
                                    'leaving_time': '{}:{}'.format(leaving_avg_time.hour, leaving_avg_time.minute)},
                                    'error': None}, status=status.HTTP_200_OK)

    '''
        *period value pattern is pipe seperated:
            a.for the quarter would be the year piped by the quarter, ex: 2019|1 (Year 2019 the first quarter)
            b.for the week would be the date(year/month/day) which will represent the first day of the week
    '''

    @action(methods=['GET'], detail=True, permission_classes=[IsAuthenticated],
            url_path='work-hours', url_name='work_avg')
    def get_work_hour_in_period(self, request, pk=None):
        try:
            employee = Employee.objects.get(id=pk)
        except Employee.DoesNotExist:
            employee = None
        if employee is None:
            return Response({'error': 'Employee is not found for id {}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        period_value = request.query_params['period_value'] if 'period_value' in request.query_params else None
        period_type = request.query_params['period_type'] if 'period_type' in request.query_params else None
        if period_value is None or period_type is None:
            return Response({'error': 'Either period_value or period_value type is missing'},
                            status=status.HTTP_400_BAD_REQUEST)
        emp_working_hours = None
        if period_type == 'year':
            try:
                int(period_value)
            except ValueError:
                return Response({'error': 'period value is invalid, year input should be only digits, ex:2019'},
                         status=status.HTTP_400_BAD_REQUEST)
            if employee.workinghours_set.all().count() > 0:
                emp_working_hours = employee.workinghours_set.all().filter(date__year=period_value).aggregate(
                    Sum('hours'))

        elif period_type == 'quarter':
            if len(period_value.split('|')) != 2:
                return Response(
                    {'error': 'period value is invalid, quarter input should be year piped by quarter, ex: 2019|3'},
                    status=status.HTTP_400_BAD_REQUEST)
            year = period_value.split('|')[0]
            quarter = period_value.split('|')[1]
            try:
                int(year)
                int(quarter)
                if not (1 <= int(quarter) <= 4):
                    raise ValueError()
            except ValueError:
                return Response(
                    {'error': 'period value is invalid, quarter input should be year piped by quarter, ex: 2019|3'},
                    status=status.HTTP_400_BAD_REQUEST)
            if employee.workinghours_set.all().count() > 0:
                emp_working_hours = employee.workinghours_set.all().filter(
                    date__range=['{}-{}-01'.format(year, self.YEAR_QUARTERS[quarter][0]),
                                 '{}-{}-01'.format(year,self.YEAR_QUARTERS[quarter][1])]).\
                                    aggregate(Sum('hours'))

        elif period_type == 'week':
            try:
                date_value = datetime.strptime(period_value, '%Y-%m-%d')
            except ValueError:
                return Response({'error': 'period value is invalid, week input should be date dash seperated, ex: 2019-3-18'},
                         status=status.HTTP_400_BAD_REQUEST)
            if employee.workinghours_set.all().count() > 0:
                emp_working_hours = employee.workinghours_set.all().\
                    filter(date__range=[date_value,date_value + timedelta(weeks=1)]).aggregate(Sum('hours'))

        if emp_working_hours is None:
            return Response({'error': 'prod type is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'result': emp_working_hours['hours__sum'], 'error': None}, status=status.HTTP_200_OK)

    def get_dates_avg(self, dates):
        sum = 0
        for date in dates:
            sum += date[0].timestamp()
        return datetime.fromtimestamp(sum / len(dates))


'''
Since we talking about team working hours percent I assumed day working hours is 8,
and took working hour for each day then calculated percentage.
I hope it does make sense :/.
'''


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_team_work_percent(request):
    if WorkingHours.objects.all().count() == 0:
        return Response({'error': 'There is no work hours data'}, status=status.HTTP_400_BAD_REQUEST)

    team_work_hours_sum = WorkingHours.objects.all().aggregate(Sum('hours'))
    total_hours = WorkingHours.objects.all().count() * 8
    team_work_percent = team_work_hours_sum['hours__sum'] / total_hours * 100
    return Response({'result': '{}%'.format(team_work_percent)}, status=status.HTTP_200_OK)
