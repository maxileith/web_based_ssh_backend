from django.core.exceptions import PermissionDenied
from django.contrib import auth


class TokenMiddleware():

    get_response = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            token = request.headers["Token"]
        except KeyError:
            raise PermissionDenied

        user = auth.authenticate(token=token)

        if not user:
            raise PermissionDenied

        request.user = user

        return self.get_response(request)
