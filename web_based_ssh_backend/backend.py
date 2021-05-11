from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
import jwt
from web_based_ssh_backend.settings import SECRET_KEY


class AuthBackend(BaseBackend):
    """Custom authentication backend using JWT token"""
    def authenticate(self, request, token=None):
        """authenticate [summary]

        - verifies the JWT token and collects user information
        - finds user in db by name which was stored inside JWT

        Args:
            request (request): request object of the http request
            token (JWT): authentication of user

        Returns:
            User: returns corresponding user
        """

        try:
            username = jwt.decode(token, SECRET_KEY, algorithms=[
                                  "HS256"])['username']
        except Exception:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        return user
