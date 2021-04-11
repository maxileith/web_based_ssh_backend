import json
import socket
import sys
import os
from paramiko.py3compat import input as prompt_input, u
import termios
import tty
import select
from time import sleep
import queue
from io import StringIO

import paramiko


class SSHClient:

    INTERVAL = .02

    def __init__(self, consumer, hostname='localhost', username='root', password='', port=22, rsa_path=None):
        self.consumer = consumer
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.rsa_path = rsa_path
        self.input_queue = queue.Queue()
        self.running = True

    def run(self):
        self.client = paramiko.SSHClient()
        self.__load_host_keys()
        # if not self.__is_host_key_valid():
        #    return
        # self.__print("1")
        self.client.connect(hostname=self.hostname, username=self.username,
                            password=self.password, port=self.port, key_filename=self.rsa_path)
        # self.__print("2")
        self.__interactive_shell()
        self.client.close()

    def input(self, x):
        self.input_queue.put(x)

    def stop(self):
        self.running = False

    def __load_host_keys(self):
        # get the current working directory
        working_dir = os.path.dirname(os.path.realpath(__file__))
        # name of known hosts file
        file_name = "known_hosts"
        complete_path = os.path.join(working_dir, file_name)
        # load host keys
        self.client.load_host_keys(complete_path)

    def __print(self, txt):
        self.__send(u(txt))

    def __println(self, txt):
        self.__print(txt)
        self.__send(u('\r\n'))

    def __prompt(self, prompt):
        # send text
        self.__print(prompt)
        response_stream = StringIO()

        while self.running:
            sleep(self.INTERVAL)

            if not self.input_queue.empty():
                r = u(self.input_queue.get())
                if r == '\r':
                    break
                response_stream.write(r)
                response_stream.flush()
                self.__send(r)

        response_text = response_stream.getvalue()
        response_stream.close()

        return response_text

    def __interactive_shell(self):
        channel = self.client.invoke_shell()

        while not channel.closed and self.running:
            sleep(self.INTERVAL)

            # output of client
            if channel.recv_ready():
                r = u(channel.recv(1024))
                self.__send(r)

            # input to client
            if channel.send_ready() and not self.input_queue.empty():
                channel.send(u(self.input_queue.get()))

    def __send(self, x):
        self.consumer.send(text_data=json.dumps({
            'data': x
        }))


class SSSHClient:

    def __init__(self, hostname, username='root', password='', port=22, rsa_path=None, rsa_password='', output=sys.stdout, input=sys.stdin):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.rsa_path = rsa_path
        self.rsa_password = rsa_password
        self.output = output
        self.input = input

    def verify_host_key(self, t):
        working_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "known_hosts"
        complete_path = os.path.join(working_dir, file_name)
        keys = paramiko.util.load_host_keys(complete_path)

        key = t.get_remote_server_key()

        if self.hostname not in keys or key.get_name() not in keys[self.hostname]:
            self.output.write(
                f"*** Warning: Unknown host key: {key.get_base64()}")
            add = prompt_input("Add the host key to known hosts? (y/N): ")

            if add.capitalize() == 'Y':
                keys.add(hostname=self.hostname, keytype='ssh-rsa', key=key)
                keys.save(complete_path)
                self.output.write("*** INFO: Added host key to known hosts!")
            else:
                sys.exit(1)

        elif keys[self.hostname][key.get_name()] != key:
            self.output.write("*** Warning: Host key has changed!")
            self.output.write(
                f"*** Old Key: {keys[self.hostname][key.get_name()].get_base64()}")
            self.output.write(f"*** New Key: {key.get_base64()}")
            update = prompt_input("Update the host key? (y/N): ")

            if update.capitalize() == 'Y':
                del keys[self.hostname]
                keys.add(hostname=self.hostname, keytype='ssh-rsa', key=key)
                keys.save(complete_path)
                self.output.write("*** Info: Host key updated!")
            else:
                sys.exit(1)

    def authentication(self, t):
        if self.rsa_path != None:
            # RSA Key
            key = paramiko.RSAKey.from_private_key_file(
                self.rsa_path, self.rsa_password)
            t.auth_publickey(self.username, key)
        else:
            # Password
            t.auth_password(self.username, self.password)
        if not t.is_authenticated():
            self.output.write("*** Authentication failed.")
            t.close()
            sys.exit(1)
        return t

    def interactive_shell(self, chan):
        oldtty = termios.tcgetattr(self.input)
        try:
            tty.setraw(self.input.fileno())
            tty.setcbreak(self.input.fileno())
            chan.settimeout(10)

            while True:
                r, _, _ = select.select([chan, self.input], [], [])
                if chan in r:
                    try:
                        x = u(chan.recv(1024))
                        if len(x) == 0:
                            break
                        self.output.write(x)
                        self.output.flush()
                    except socket.timeout:
                        pass
                if self.input in r:
                    x = self.input.read(1)
                    if len(x) == 0:
                        break
                    chan.send(x)

        finally:
            termios.tcsetattr(self.input, termios.TCSADRAIN, oldtty)

    def start(self):
        # setup logging
        paramiko.util.log_to_file("demo.log")

        # now connect
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.hostname, self.port))
        except Exception as e:
            self.output.write("*** Connect failed: " + str(e))
            sys.exit(1)

        try:
            t = paramiko.Transport(sock)
            try:
                t.start_client()
            except paramiko.SSHException:
                self.output.write("*** SSH negotiation failed.")
                sys.exit(1)

            self.verify_host_key(t)

            t = self.authentication(t)

            chan = t.open_session()
            chan.get_pty()
            chan.invoke_shell()

            self.interactive_shell(chan)
            chan.close()
            t.close()

        except Exception as e:
            self.output.write("*** Caught exception: " +
                              str(e.__class__) + ": " + str(e))
            try:
                t.close()
            except:
                pass
            sys.exit(1)
