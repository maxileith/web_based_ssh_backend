from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    token = models.CharField(max_length=500)
    user = models.OneToOneField(User, on_delete=models.deletion.CASCADE)
