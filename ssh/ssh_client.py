import json
import socket
import sys
import os
from paramiko.py3compat import input as prompt_input, u
import termios
import tty
import select
from time import sleep

import paramiko


def ssh_task(consumer):
    client = paramiko.client.SSHClient()

    # loading custom host keys file
    working_dir = os.path.dirname(os.path.realpath(__file__))
    file_name = "known_hosts"
    complete_path = os.path.join(working_dir, file_name)
    client.load_host_keys(complete_path)

    client.connect(hostname='10.0.0.3', username="root", password="")

    channel = client.invoke_shell()

    while not channel.closed and consumer.run:

        sleep(.02)

        # output of client
        if channel.recv_ready():
            r = u(channel.recv(1024))
            consumer.send(text_data=json.dumps({
                'data': r
            }))

        # input to client
        if channel.send_ready() and not consumer.input_queue.empty():
            channel.send(u(consumer.input_queue.get()))

    client.close()


"""
class SSHClient:

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

if __name__ == '__main__':
    client = SSHClient(hostname='10.0.0.3')
    client.start()
"""
