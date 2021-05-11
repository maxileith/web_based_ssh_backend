import os
import uuid

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import ManyToOneRel
from django.utils.deconstruct import deconstructible


@deconstructible
class RenamePath:
    """Wrapper around a function to rename files before saving"""

    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        filename = uuid.uuid4()
        return os.path.join(self.path, str(filename) + ".key")


rename_path = RenamePath('known_hosts/')


class KnownHost(models.Model):
    """Represents a known host file. Each user has only one file."""
    # CASCADE --> delete entity if the corresponding user is to be deleted
    user = models.OneToOneField(User, on_delete=models.deletion.CASCADE)
    file = models.FileField(upload_to=rename_path)
