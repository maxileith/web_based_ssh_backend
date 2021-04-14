import json
from channels.generic.websocket import WebsocketConsumer
import threading

from .ssh_client import SSHClientController


class SSHConsumer(WebsocketConsumer):

    def connect(self):
        self.ssh_client = SSHClientController(
            self, user_id=1, hostname="10.0.0.3", username="root", password="")

        self.accept()

        self.thread = threading.Thread(target=self.ssh_client.run)
        self.thread.start()

    def receive(self, text_data):
        self.ssh_client.input(json.loads(text_data)["data"])

    def disconnect(self, close_code):
        self.ssh_client.stop()
