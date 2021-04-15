from django.core.exceptions import PermissionDenied
from django.contrib import auth
from channels.db import database_sync_to_async


class TokenMiddleware:

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
            token = request.COOKIES["token"]
            user = auth.authenticate(token=token)
        except KeyError:
            user = None

        if not user:
            raise PermissionDenied

        request.user = user

        return self.get_response(request)


@database_sync_to_async
def authenticate(token):
    return auth.authenticate(token=token)


class WSTokenMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            token = scope['cookies']['token']
            user = await authenticate(token=token)
        except KeyError:
            user = None

        if not user:
            raise PermissionDenied

        scope['user'] = user

        return await self.app(scope, receive, send)


class DisableCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response
