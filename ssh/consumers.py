import json

from channels.generic.websocket import WebsocketConsumer
import threading
from paramiko.py3compat import u
import os

import paramiko
import threading
import sys

import queue

from time import sleep

from .ssh_client import AppSSHClient


class SSHConsumer(WebsocketConsumer):

    run = True

    input_queue = queue.Queue()
    lock = threading.Lock()

    def connect(self):
        self.accept()
        client = threading.Thread(target=self.ssh_task)
        client.start()

    def receive(self, text_data):
        self.lock.acquire()
        self.input_queue.put(json.loads(text_data)["data"])
        self.lock.release()

    def disconnect(self, close_code):
        self.run = False
        pass

    def ssh_task(self):
        client = paramiko.client.SSHClient()

        # loading custom host keys file
        working_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "known_hosts"
        complete_path = os.path.join(working_dir, file_name)
        client.load_host_keys(complete_path)

        client.connect(hostname='10.0.0.3', username="root", password="")

        channel = client.invoke_shell()

        while not channel.closed and self.run:

            sleep(.02)

            # output of client
            while channel.recv_ready():
                r = u(channel.recv(1024))
                sys.stdout.write(r)
                sys.stdout.flush()
                self.send(text_data=json.dumps({
                    'data': r
                }))

            # input to client
            self.lock.acquire()
            while channel.send_ready() and not self.input_queue.empty():
                char = self.input_queue.get()
                channel.send(u(char))
            self.lock.release()

        client.close()
