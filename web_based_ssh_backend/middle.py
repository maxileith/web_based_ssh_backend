from django.core.exceptions import PermissionDenied
from django.contrib import auth
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from app_auth.models import Token


class TokenMiddleware:
    """TokenMiddleware [summary]

    - middleware that extracts the jwt token from the request
    - checks if token is valid


    """

    get_response = None

    # these paths must be reachable without a token
    WHITELIST = [
        '/auth/register/',
        '/auth/login/',
        '/admin/',
        '/auth/email/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        for e in self.WHITELIST:
            if e in request.META['PATH_INFO']:
                return self.get_response(request)

        # get user by token, otherwise raise PermissionDenied
        try:
            token = request.headers['token']

            token_object = Token.objects.filter(token=token).first()

            if token_object and token_object.active:
                user = auth.authenticate(token=token)
            else:
                user = None
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
    """Verifies JWT token for WebSocket Backend"""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """__call__ [summary]

        verifies supplied JWT Token and authenticates user
        - read JWT from query parameters
        - authenticate user using JWT

        Note: arguments are required by framework
        Args:
            scope: stores current variables
            receive: receive data
            send: send data

        Returns:
            App: returns app
        """

        # get user by token, otherwise raise PermissionDenied
        try:
            # token in URL, because WS in JavaScript does not allow to add
            # custom headers
            token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]
            user = await authenticate(token=token)
        except KeyError:
            user = None

        if not user:
            raise PermissionDenied

        scope['user'] = user

        return await self.app(scope, receive, send)


class DisableCSRFMiddleware:
    """Disables CSRF verification - not needed since JWTs are used"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response
