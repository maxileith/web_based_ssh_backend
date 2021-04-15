import json
from channels.generic.websocket import WebsocketConsumer
import threading

from .ssh_client import SSHClientController


class SSHConsumer(WebsocketConsumer):

    http_user = True

    def connect(self):
        self.ssh_session_id = self.scope['url_route']['kwargs']['ssh_session_id']

        print(self.scope["user"])

        self.ssh_client = SSHClientController(
            self, user_id=self.ssh_session_id, hostname="10.0.0.3", username="root", password="")

        self.accept()

        self.thread = threading.Thread(target=self.ssh_client.run)
        self.thread.start()

    def receive(self, text_data):
        self.ssh_client.input(json.loads(text_data)["data"])

    def disconnect(self, close_code):
        self.ssh_client.stop()
