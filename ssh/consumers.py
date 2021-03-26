import json
from channels.generic.websocket import WebsocketConsumer
from .ssh_client import SSHClient
import io
import threading


class SSHConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(text_data)

        text_data_json = json.loads(text_data)


        #self.input.write(text_data_json['keyCode'].to_bytes(
        #    1, byteorder='big', signed=False))
        #self.input.flush()

        self.send(text_data=json.dumps({
            'ascii': text_data_json["ascii"]
        }))
