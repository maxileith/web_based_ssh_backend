from auth.serializers import UserSerializer
from .models import SSHSession
from rest_framework import serializers
from django.contrib.auth.models import User


class SSHSessionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, allow_blank=True)

    class Meta:
        model = SSHSession
        fields = ('title', 'hostname', 'port', 'username', 'description', 'password')

    # there should probably be also a partial update method
    def update(self, instance, validated_data):
        instance.title = validated_data.pop('title')
        instance.password = validated_data.pop('password')
        instance.username = validated_data.pop('username')
        instance.port = validated_data.pop('port')
        instance.description = validated_data.pop('description')
        instance.hostname = validated_data.pop('hostname')

        instance.save()
        return instance

    def create(self, validated_data):
        print(validated_data)
        instance = SSHSession.objects.create()
        instance.title = validated_data.pop('title')
        instance.password = validated_data.pop('password')
        instance.username = validated_data.pop('username')
        p = validated_data.pop('port')
        instance.port = p
        instance.description = validated_data.pop('description')
        instance.hostname = validated_data.pop('hostname')
        instance.save()

        return instance
