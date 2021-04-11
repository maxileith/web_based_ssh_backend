"""
ASGI config for web_based_ssh_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from django.core.asgi import get_asgi_application

from ssh import routing, consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'web_based_ssh_backend.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns,
        )
    ),
    # 'channel': ChannelNameRouter({
    #    "ssh-session": consumers.SSHSessionConsumer.as_asgi(),
    # })
})
# application = get_asgi_application()
