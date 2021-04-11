import json
from channels.generic.websocket import WebsocketConsumer
import threading
import queue

from .ssh_client import ssh_task


class SSHConsumer(WebsocketConsumer):

    def connect(self):
        self.run = True
        self.input_queue = queue.Queue()
        self.thread = threading.Thread(target=ssh_task, args=(self,))
        self.thread.start()
        self.accept()

    def receive(self, text_data):
        self.input_queue.put(json.loads(text_data)["data"])

    def disconnect(self, close_code):
        self.run = False
        pass
