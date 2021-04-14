from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
import jwt


class AuthBackend(BaseBackend):
    def authenticate(self, request, token=None):

        try:
            username = jwt.decode(token,
                                  "ha", algorithms=["HS256"])['username']
        except Exception:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        return user
