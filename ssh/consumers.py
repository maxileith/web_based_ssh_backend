import json

from channels.consumer import SyncConsumer
from channels.generic.websocket import WebsocketConsumer
from io import StringIO
import threading
from asgiref.sync import async_to_sync

import queue

from .ssh_client import AppSSHClient


class SSHConsumer(WebsocketConsumer):

    ssh_threads = []
    run = True

    output_queue = queue.Queue()
    input_queue = queue.Queue()

    def connect(self):
        self.accept()
        new_client = AppSSHClient(self)
        new_client.start()
        self.ssh_threads.append(new_client)

    def disconnect(self, close_code):
        self.run = False
        pass

    def receive(self, text_data):
        # print(text_data)

        text_data_json = json.loads(text_data)
        self.input_queue.put(text_data_json["data"])

        while not self.output_queue.empty():
            tmp = self.output_queue.get()
            print(tmp, end='')
            self.send(text_data=json.dumps({
                'data': tmp
            }))

        """
        self.send(text_data=json.dumps({
            'data': text_data_json["data"]
        }))

        async_to_sync(self.channel_layer.send)(
            "ssh-session",
            {
                "type": "test.print",
                "text": "blabla",
            }
        )
        """


class SSHSessionConsumer(SyncConsumer):
    def test_print(self, message):
        print("Test: ", message["text"])
