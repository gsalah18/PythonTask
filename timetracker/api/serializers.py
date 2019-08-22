from rest_framework import serializers

from timetracker.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'dateadded'
        ]
