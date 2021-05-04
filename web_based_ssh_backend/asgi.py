"""
ASGI config for web_based_ssh_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'web_based_ssh_backend.settings')
django.setup()

from .middle import WSTokenMiddleware
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import ssh.routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        WSTokenMiddleware(
            URLRouter(
                ssh.routing.websocket_urlpatterns,
            )
        )
    )
})
