import json
from datetime import timedelta
from datetime import datetime

from django.db.models import Sum, F, Avg, Max, Min
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from timetracker.models import Employee, Checking
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
        check = request.data.get('check', '')
        time = datetime.now().timestamp()
        try:
            employee = Employee.objects.get(id=pk)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee is not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            last_check = employee.checking_set.all().latest('id')
        except Checking.DoesNotExist:
            last_check = None

        if check == '':
            return Response({'error': 'Check type is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        if check == 'in':
            if last_check is None or last_check.checkout is not None:
                checking_serializer = CheckingSerializer(data={'checkin': time, 'employee': pk})
                if checking_serializer.is_valid():
                    checking_serializer.save()
                    return Response({'result': checking_serializer.data, 'error': None}, status=status.HTTP_201_CREATED)
                return Response({'error': json.dumps(checking_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'You have to check out first then check in'},
                                status=status.HTTP_400_BAD_REQUEST)

        if check == 'out':
            if last_check.checkout is None:
                checking_serializer = CheckingSerializer(last_check, data={'employee': last_check.employee_id,
                                                                           'checkin': last_check.checkin,
                                                                           'checkout': time})
                if checking_serializer.is_valid():
                    checking_serializer.save()
                    return Response({'result': checking_serializer.data, 'error': None}, status=status.HTTP_200_OK)
                return Response({'error': json.dumps(checking_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'You have to check in first then check out'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Check va;ie is invalid'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated],
            url_path='set-vacation', url_name='set_vacation')
    def set_vacation(self, request, pk=None):
        try:
            datetime.strptime(request.data.get('date', ''), '%Y-%m-%d')
        except ValueError:
            return Response({'error': 'Date is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        vacation_serializer = VacationSerializer(
            data={'employee': pk,
                  'description': request.data.get('description', ''),
                  'date': datetime.strptime(request.data.get('date', None), '%Y-%m-%d').date()})
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
            return Response({'error': 'Employee is not found for id {}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        emp_hours_avg = employee.checking_set.all().exclude(checkout__isnull=True) \
            .annotate(arrive_avg=Avg('checkin'), leave_avg=Avg('checkout'))
        if emp_hours_avg.count() == 0:
            return Response({'error': 'There is no checkout Data'}, status=status.HTTP_400_BAD_REQUEST)

        arrival_avg_time = datetime.fromtimestamp(emp_hours_avg[0].arrive_avg)
        leaving_avg_time = datetime.fromtimestamp(emp_hours_avg[0].leave_avg)
        return Response({'result': {'arrival_time': '{}:{}'.format(arrival_avg_time.hour, arrival_avg_time.minute),
                                    'leaving_time': '{}:{}'.format(leaving_avg_time.hour, leaving_avg_time.minute)},
                         'error': None}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, permission_classes=[IsAuthenticated],
            url_path='work-hours', url_name='work_avg')
    def get_work_hour_in_period(self, request, pk=None):
        try:
            employee = Employee.objects.get(id=pk)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee is not found for id {}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        period_value = request.query_params['period_value'] if 'period_value' in request.query_params else None
        period_type = request.query_params['period_type'] if 'period_type' in request.query_params else None
        if period_value is None or period_type is None:
            return Response({'error': 'Either period_value or period_value type is missing'},
                            status=status.HTTP_400_BAD_REQUEST)
        emp_working_hours = None
        if period_type == 'year':
            try:
                year = int(period_value)
            except ValueError:
                return Response({'error': 'period value is invalid, year input should be only digits, ex:2019'},
                                status=status.HTTP_400_BAD_REQUEST)
            year_begin = datetime(year=year, month=1, day=1).timestamp()
            year_end = datetime(year=year, month=12, day=31, hour=23, minute=59, second=59).timestamp()
            if employee.checking_set.all().count() > 0:
                emp_working_hours = employee.checking_set.all().exclude(checkout__isnull=True) \
                    .filter(checkin__gte=year_begin, checkin__lte=year_end,
                            checkout__gte=year_begin, checkout__lte=year_end).annotate(
                    working_hours=Sum(F('checkout') - F('checkin')))

        elif period_type == 'quarter':
            if len(period_value.split('|')) != 2:
                return Response(
                    {'error': 'period value is invalid, quarter input should be year piped by quarter, ex: 2019|3'},
                    status=status.HTTP_400_BAD_REQUEST)
            year = period_value.split('|')[0]
            quarter = period_value.split('|')[1]
            try:
                year = int(year)
                quarter = int(quarter)
                if not (1 <= int(quarter) <= 4):
                    raise ValueError()
            except ValueError:
                return Response(
                    {'error': 'period value is invalid, quarter input should be year piped by quarter, ex: 2019|3'},
                    status=status.HTTP_400_BAD_REQUEST)
            quarter_begin = datetime(year=year, month=self.YEAR_QUARTERS[quarter][0], day=1).timestamp()
            quarter_end = (datetime(year=year, month=self.YEAR_QUARTERS[quarter][0], day=1) + timedelta(
                months=1)).timestamp()
            if employee.workinghours_set.all().count() > 0:
                emp_working_hours = employee.checking_set.all().exclude(checkout__isnull=True) \
                    .filter(checkin__gte=quarter_begin, checkin__lte=quarter_end,
                            checkout__gte=quarter_begin, checkout__lte=quarter_end).annotate(
                    working_hours=Sum(F('checkout') - F('checkin')))
        elif period_type == 'week':
            try:
                date_value = datetime.strptime(period_value, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {'error': 'period value is invalid, week input should be date dash seperated, ex: 2019-3-18'},
                    status=status.HTTP_400_BAD_REQUEST)
            week_brgin = date_value.timestamp()
            week_end = (date_value + timedelta(weeks=1)).timestamp()
            if employee.workinghours_set.all().count() > 0:
                emp_working_hours = employee.checking_set.all().exclude(checkout__isnull=True) \
                    .filter(checkin__gte=week_brgin, checkin__lte=week_end,
                            checkout__gte=week_brgin, checkout__lte=week_end).annotate(
                    working_hours=Sum(F('checkout') - F('checkin')))
        if emp_working_hours is None:
            return Response({'error': 'prod type is not valid'}, status=status.HTTP_400_BAD_REQUEST)
        if emp_working_hours.count() == 0:
            return Response({'error': 'There is no data in the period'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'result': datetime.fromtimestamp(emp_working_hours[0].working_hours).hour - 2, 'error': None},
                        status=status.HTTP_200_OK)
        # The -2 is because its taking 2 hours plus due to the GTM timing


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_team_work_percent(request):
    if Checking.objects.all().count() == 0:
        return Response({'error': 'There is no work hours data'}, status=status.HTTP_400_BAD_REQUEST)

    team_work_hours_sum = datetime.fromtimestamp(Checking.objects.all().aggregate(hours_sum=Sum(F('checkout') - F('checkin')))['hours_sum']).hour - 2
    # The -2 is because its taking 2 hours plus due to the GTM timing
    total_hours = datetime.fromtimestamp((Checking.objects.all().aggregate(total_hours=Max('checkout') - Min('checkin')))['total_hours']).day * 8
    team_work_percent = team_work_hours_sum / total_hours * 100
    return Response({'result': '{}%'.format(team_work_percent)}, status=status.HTTP_200_OK)
