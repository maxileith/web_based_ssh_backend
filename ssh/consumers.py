import json

from channels.consumer import SyncConsumer, AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer


class SSHClientConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "ssh-group"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.send(
            "ssh-session",
            {
                "type": "update",
                "message": "ha",
            }
        )

        await self.channel_layer.group_send(self.group_name, {
            'type': 'ssh_group_message_received',
            'message': message,
        })

    async def ssh_group_message_received(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
        }))


class SSHSession(SyncConsumer):
    def update(self, message):
        print("in here")
        print("Test", message)
