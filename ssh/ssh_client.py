import json
import os
from paramiko.py3compat import u
from time import sleep
import queue
from io import StringIO
import paramiko


class SSHClientController:

    FPS = 30
    INTERVAL = 1.0/FPS
    TIMEOUT = 15

    def __init__(self, consumer, hostname=None, username=None, password=None, port=22, rsa_path=None):
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
            self.consumer.close()
            return
        self.__interactive_shell()
        self.client.close()
        self.consumer.close()

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
        self.__println("establishing the connection ...")
        try:
            self.client.connect(hostname=self.hostname, username=self.username,
                                password=self.password, port=self.port,
                                key_filename=self.rsa_path, timeout=self.TIMEOUT,
                                look_for_keys=False, auth_timeout=self.TIMEOUT)
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
                if len(r) == 0:
                    break
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
