import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.deconstruct import deconstructible
# Create your models here.


@deconstructible
class RenamePath:
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        filename = uuid.uuid4()
        return os.path.join(self.path, str(filename) + ".key")


rename_path = RenamePath('ssh_keys/')


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
    key_file = models.FileField(upload_to=rename_path, blank=True)

    def __str__(self):
        return self.title


