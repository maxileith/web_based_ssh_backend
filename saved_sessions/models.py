from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class SSHSession(models.Model):
    """"
        Simple Model to store information about a SSH Session
        ID field is automatically added by Django
    """
    title = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    port = models.IntegerField(null=True)
    username = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    password = models.CharField(max_length=500)
    user = models.OneToOneField(User, on_delete=models.deletion.CASCADE)

    def __str__(self):
        return self.title
