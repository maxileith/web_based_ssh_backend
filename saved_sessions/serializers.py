from .models import SSHSession
from rest_framework import serializers
from django.contrib.auth.models import User


class SSHSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = SSHSession
        fields = ('title', 'hostname', 'port', 'username', 'description')

