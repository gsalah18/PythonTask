from rest_framework import serializers

from timetracker.models import Employee
from timetracker.models import Checking
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
            'userid',
            'check',
            'time'
        ]

class VacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacation
        fields = [
            'id',
            'userid',
            'description',
            'date'
        ]
