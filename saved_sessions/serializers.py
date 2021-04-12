from .models import SSHSession
from rest_framework import serializers
from django.contrib.auth.models import User


class SSHSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    password = serializers.CharField(max_length=255, allow_blank=True)

    class Meta:
        model = SSHSession
        fields = ('title', 'hostname', 'port', 'username', 'description', 'password')

    # there should probably be also a partial update method
    def update(self, instance, validated_data):
        instance.title = validated_data.pop('title')
        instance.password = validated_data.pop('password')
        user = validated_data.pop('user')
        instance.username = user['username']
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
        #user = validated_data.pop('user')
        #username = user['username']
        #instance.user = User.objects.filter(username=username)
        instance.port = int(validated_data.pop('port'))
        instance.description = validated_data.pop('description')
        instance.hostname = validated_data.pop('hostname')
        instance.save()

        return instance
