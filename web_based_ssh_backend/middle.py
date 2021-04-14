from django.core.exceptions import PermissionDenied
from django.contrib import auth


class TokenMiddleware():

    get_response = None

    WHITELIST = [
        '/auth/login/',
        '/admin/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        for e in self.WHITELIST:
            if e in request.META['PATH_INFO']:
                return self.get_response(request)

        try:
            token = request.headers["Token"]
            user = auth.authenticate(token=token)
        except KeyError:
            user = None

        if not user:
            raise PermissionDenied

        request.user = user

        return self.get_response(request)


class DisableCSRFMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response
