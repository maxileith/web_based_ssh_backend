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
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)
    password = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.deletion.CASCADE)
    # key_file = models.FilePathField(blank=True)

    def __str__(self):
        return self.title
