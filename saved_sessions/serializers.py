from .models import SSHSession
from rest_framework import serializers


class SSHSessionSerializer(serializers.ModelSerializer):
    """Serializes SSHSessions to JSON

        - fields listed below are inside JSON
        - Note: field key_file describes whether the key file exists
    """
    password = serializers.CharField(max_length=255, allow_blank=True)
    key_file = serializers.BooleanField(required=False)

    class Meta:
        model = SSHSession
        fields = ('id', 'title', 'hostname', 'port',
                  'username', 'description', 'password', 'key_file')

    def create(self, validated_data):
        """create [summary]

        creates new SSHSession object from JSON
        - reads value from JSON and assigns it to the object

        Args:
            validated_data: validated by djangorestframework

        Returns:
            SSHSession: returns newly created SSHSession
        """

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
    """Serializes SSHSessions to JSON

           - same behaviour as SSHSessionSerializer
           -> BUT removes password field from output
    """

    class Meta:
        model = SSHSession
        fields = ('id', 'title', 'hostname', 'port',
                  'username', 'description', 'key_file')
