from rest_framework import serializers

from timetracker.models import Employee
from timetracker.models import Checking
from timetracker.models import WorkingHours
from timetracker.models import Vacation


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id',
            'name'
        ]


class CheckingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checking
        fields = [
            'id',
            'employee',
            'check',
            'time'
        ]


class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = [
            'id',
            'employee',
            'hours',
            'date'
        ]


class VacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacation
        fields = [
            'id',
            'employee',
            'description',
            'date'
        ]
