from .models import SSHSession
from rest_framework import serializers


class SSHSessionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, allow_blank=True)
    key_file = serializers.BooleanField()

    class Meta:
        model = SSHSession
        fields = ('id', 'title', 'hostname', 'port',
                  'username', 'description', 'password')

    def create(self, validated_data):
        instance = SSHSession.objects.create(user=self.context['user'])
        instance.title = validated_data.pop('title')
        instance.password = validated_data.pop('password')
        instance.username = validated_data.pop('username')
        instance.port = validated_data.pop('port')
        instance.description = validated_data.pop('description')
        instance.hostname = validated_data.pop('hostname')
        instance.save()

        return instance


class RedactedSSHSessionSerializer(SSHSessionSerializer):
    class Meta:
        model = SSHSession
        fields = ('id', 'title', 'hostname', 'port',
                  'username', 'description', 'key_file')
