import json
from channels.generic.websocket import WebsocketConsumer
import threading

from saved_sessions.models import SSHSession

from .ssh_client import SSHClientController


class SSHConsumer(WebsocketConsumer):

    http_user = True

    def connect(self):
        self.ssh_client = None

        ssh_session_id = self.scope['url_route']['kwargs']['ssh_session_id']
        self.user = self.scope['user']

        self.session_data = self.__get_session_data(self.user, ssh_session_id)

        if not self.session_data:
            self.close()
            return

        self.ssh_client = SSHClientController(
            self, user_id=self.user.id, hostname=self.session_data.hostname,
            username=self.session_data.username, password=self.session_data.password)

        self.accept()

        self.thread = threading.Thread(target=self.ssh_client.run)
        self.thread.start()

    def receive(self, text_data):
        self.ssh_client.input(json.loads(text_data)["data"])

    def disconnect(self, close_code):
        if self.ssh_client:
            self.ssh_client.stop()

    def __get_session_data(self, user, session_id):
        return SSHSession.objects.filter(user=user, id=session_id).first()
