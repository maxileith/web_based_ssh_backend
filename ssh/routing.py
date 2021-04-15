from django.urls import path

from .consumers import SSHConsumer

websocket_urlpatterns = [
    path(r'ws/ssh/<int:ssh_session_id>', SSHConsumer.as_asgi()),
]
