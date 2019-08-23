from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from timetracker.models import Employee
from timetracker.models import Checking
from timetracker.models import WorkingHours
from timetracker.models import Vacation


class EmployeeTestCase(APITestCase):
    def setUp(self):
        # User and Token Authentication Setup
        self.superuser = User.objects.create_superuser('admin', 'admin', 'admin')
        auth_url = 'http://localhost:8000/timetracker/api/v1/auth'
        auth_response = self.client.post(auth_url, {'username': 'admin', 'password': 'admin'})
        self.auth_token = auth_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.auth_token))

        # Employee Model Setup
        emp1 = Employee.objects.create(name='Salah')
        emp2 = Employee.objects.create(name='Waseem')

        # Checking Model Setup
        Checking.objects.create(employee=emp1, check='in', time=timezone.now())
        Checking.objects.create(employee=emp1, check='out', time=timezone.now() + timedelta(hours=8))
        Checking.objects.create(employee=emp2, check='in', time=timezone.now())
        Checking.objects.create(employee=emp2, check='out', time=timezone.now() + timedelta(hours=8))

        # WorkingHours Model Setup
        WorkingHours.objects.create(employee=emp1, hours=8, date=timezone.now())
        WorkingHours.objects.create(employee=emp2, hours=8, date=timezone.now())
        working_hours = WorkingHours.objects.all()

        # Vacation Model Setup
        Vacation.objects.create(employee=emp1, description='Salah Vacation', date=datetime(year=2019, month=8, day=29))
        Vacation.objects.create(employee=emp2, description='Salah Vacation', date=datetime(year=2019, month=8, day=25))
        vacations = Vacation.objects.all()

    def test_employees_info(self):
        employees = Employee.objects.all()
        self.assertEqual(employees.count(), 2)
        salah = Employee.objects.get(id=1)
        waseem = Employee.objects.get(id=2)
        self.assertEqual(salah.name, 'Salah')
        self.assertEqual(waseem.name, 'Waseem')

    def test_set_check(self):
        # Correct Request
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/set-check/'.format(emp_id)
        response = self.client.post(url, {'check': 'in'})
        self.assertEqual(response.status_code, 201)
        # Wrong Employee Id
        emp_id = 10
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/set-check/'.format(emp_id)
        response = self.client.post(url, {'check': 'in'})
        self.assertEqual(response.status_code, 400)
        # No check in th body
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/set-check/'.format(emp_id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        # Wrong check value
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/set-check/'.format(emp_id)
        response = self.client.post(url, {'check': 'invalid'})
        self.assertEqual(response.status_code, 400)

    def test_set_vacation(self):
        # Correct Request
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/set-vacation/'.format(emp_id)
        response = self.client.post(url, {'date': '2019-10-25', 'description': 'The Description'})
        self.assertEqual(response.status_code, 201)
        # Wrong Employee id
        emp_id = 10
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/set-vacation/'.format(emp_id)
        response = self.client.post(url, {'date': '2019-10-25', 'description': 'The Description'})
        self.assertEqual(response.status_code, 400)
        # Empty request body
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/set-vacation/'.format(emp_id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        # Invalid date
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/set-vacation/'.format(emp_id)
        response = self.client.post(url, {'date': '2019-10-25invalid', 'description': 'The Description'})
        self.assertEqual(response.status_code, 400)


    def test_work_hours(self):
        # Correct Request
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-hours/' \
              '?period_type={}&period_value={}'.format(emp_id, 'year', '2019')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Wrong Employee Id
        emp_id = 10
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-hours/' \
              '?period_type={}&period_value={}'.format(emp_id, 'year', '2019')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        # Invalid period type
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-hours/' \
              '?period_type={}&period_value={}'.format(emp_id, 'year-invalid', '2019')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        # Invalid period value (year)
        # emp_id = 1
        # url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-hours/' \
        #       '?period_type={}&period_value={}'.format(emp_id, 'year', '2019-invalid')
        # response = self.client.get(url)
        # self.assertEqual(response.status_code, 400)
        # Invalid period value (quarter)
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-hours/' \
              '?period_type={}&period_value={}'.format(emp_id, 'quarter', '2019|3-invalid')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        # Invalid period value (week)
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-hours/' \
              '?period_type={}&period_value={}'.format(emp_id, 'week', '2019-8-23-invalid')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        # Without period type and period value
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-hours/'.format(emp_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_work_avg(self):
        # Correct Request
        emp_id = 1
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-avg/'.format(emp_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Wrong Employee Id
        emp_id = 10
        url = 'http://localhost:8000/timetracker/api/v1/employees/{}/work-avg/'.format(emp_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_team_work_percent(self):
        # Correct Request
        url = 'http://localhost:8000/timetracker/api/v1/team-work/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
