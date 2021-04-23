from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.deletion.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user)
