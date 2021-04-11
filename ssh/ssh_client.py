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


class SSHClientController:

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
        key_policy = HostKeyChecker(self.__println, self.__prompt)
        self.client.set_missing_host_key_policy(policy=key_policy)
        if not self.__connect():
            return
        self.__interactive_shell()
        self.client.close()

    def input(self, x):
        self.input_queue.put(x)

    def stop(self):
        self.running = False

    def __print(self, txt):
        self.__send(u(str(txt)))

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

        self.__send(u('\r\n'))

        return response_text

    def __connect(self):
        try:
            self.client.connect(hostname=self.hostname, username=self.username,
                                password=self.password, port=self.port, key_filename=self.rsa_path)
            return True
        except HostKeyError:
            self.__println("host key error")
        except Exception as e:
            self.__println(e)

        return False

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


class HostKeyChecker(paramiko.MissingHostKeyPolicy):
    def __init__(self, println, prompt):
        self.__println = println
        self.__prompt = prompt

    def missing_host_key(self, client, hostname, key):
        known_host_keys_path = self.__known_hosts_path()
        # load and return known host keys
        known_host_keys = paramiko.util.load_host_keys(known_host_keys_path)
        # check if key is known, changed or unknown
        case = self.__identify_case(hostname, known_host_keys, key)
        # ask the user what to do if needed
        self.__println(case)
        if case == "unknown":
            self.__handle_unknown(hostname, known_host_keys,
                                  key, known_host_keys_path)
        elif case == "changed":
            self.__handle_changed(hostname, known_host_keys,
                                  key, known_host_keys_path)

    def __known_hosts_path(self):
        # get the current working directory
        working_dir = os.path.dirname(os.path.realpath(__file__))
        # name of known hosts file
        file_name = "known_hosts"
        return os.path.join(working_dir, file_name)

    def __identify_case(self, hostname, known_host_keys, key):
        if hostname not in known_host_keys or key.get_name() not in known_host_keys[hostname]:
            # host key is new
            return "unknown"
        if known_host_keys[hostname][key.get_name()] != key:
            # host key of the host changed
            return "changed"
        # host key is known
        return "known"

    def __handle_unknown(self, hostname, known_host_keys, key, known_host_keys_path):
        self.__println(
            f'*** Warning: Unknown host key: {key.get_base64()}')
        add = self.__prompt(
            "Add the host key to known hosts? (y/N): ")

        if add.capitalize() == 'Y':
            known_host_keys.add(hostname=hostname,
                                keytype='ssh-rsa', key=key)
            known_host_keys.save(known_host_keys_path)
            self.__println(
                '*** INFO: Added host key to known hosts!')
            return

        raise HostKeyError

    def __handle_changed(self, hostname, known_host_keys, key, known_host_keys_path):
        self.__println('*** Warning: Host key has changed!')
        self.__println(
            f'*** Old Key: {known_host_keys[hostname][key.get_name()].get_base64()}')
        self.__println(f'*** New Key: {key.get_base64()}')
        update = self.__prompt('Update the host key? (y/N): ')

        if update.capitalize() == 'Y':
            del known_host_keys[hostname]
            known_host_keys.add(hostname=hostname, keytype='ssh-rsa', key=key)
            known_host_keys.save(known_host_keys_path)
            self.__println('*** Info: Host key updated!')
            return

        raise HostKeyError


class HostKeyError(Exception):
    pass


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
