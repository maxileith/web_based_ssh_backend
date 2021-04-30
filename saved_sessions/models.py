import os
import uuid
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


def upload_to(path):
    def wrapper(instance, filename):
        filename = uuid.uuid4()
        return os.path.join(path, str(filename) + ".key")
    return wrapper


class SSHSession(models.Model):
    """"
        Simple Model to store information about a SSH Session
        ID field is automatically added by Django
    """
    title = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    port = models.IntegerField(default=22)
    username = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)
    password = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.deletion.CASCADE)
    key_file = models.FileField(upload_to=upload_to("ssh_keys/"), blank=True)

    def __str__(self):
        return self.title


