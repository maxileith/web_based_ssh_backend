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
        """__init__ [summary]

        Create a controller and give it all the information needed for the connection.

        Args:
            consumer (SSHConsumer): Consumer to send the output to.
            hostname (str, optional): Hostname to which the connection is to be established. Defaults to None.
            username (str, optional): Username used to authenticate to the server. Defaults to None.
            password (str, optional): Password used to authenticate to the server. Defaults to None.
            port (int, optional): Port to which the connection is to be established. Defaults to 22.
            rsa_path (str, optional): Path to the rsa keyfile used to authenticate to the server. Defaults to None.
        """
        self.consumer = consumer
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.rsa_path = rsa_path
        self.input_queue = queue.Queue()
        self.running = True

    def run(self):
        """run [summary]

        main programme logic

        """
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
        """input [summary]

        Method to send data to the client.

        Args:
            x (str): String to be passed on to the client.
        """
        self.input_queue.put(x)

    def stop(self):
        """stop [summary]

        Disconnects from the SSH server and terminates the client.

        """
        self.running = False

    def __print(self, txt):
        """__print [summary]

        Print to consumer.

        Args:
            txt (str): Text to be printed.
        """
        self.__send(u(str(txt)))

    def __println(self, txt):
        """__println [summary]

        Analogous to __print, with newline at the end.

        Args:
            txt (str): Text to be printed.
        """
        self.__print(txt)
        self.__send(u('\r\n'))

    def __prompt(self, prompt=''):
        """__prompt [summary]

        Prompts the user to do something.

        Args:
            prompt (str, optional): Prompt text. Defaults to ''.

        Returns:
            str: Response from consumer
        """
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
        """__connect [summary]

        Establish connection and handle errors

        Returns:
            bool: True on successful connect, False otherwise
        """
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
        """__interactive_shell [summary]

        Passes data permanently from consumer to client and vice versa.

        """
        channel = self.client.invoke_shell()

        def __loop_tasks():
            while not channel.closed and self.running:
                sleep(self.INTERVAL)
                # output ot client
                while channel.recv_ready():
                    r = u(channel.recv(1024))
                    if len(r) == 0:
                        return
                    self.__send(r)

                # input from client
                while channel.send_ready() and not self.input_queue.empty():
                    channel.send(u(self.input_queue.get()))

        __loop_tasks()

    def __send(self, x):
        """__send [summary]

        Sends data to the consumer.

        Args:
            x (str): data to be send
        """
        self.consumer.send(text_data=json.dumps({
            'data': x
        }))


class HostKeyChecker(paramiko.MissingHostKeyPolicy):
    def __init__(self, println, prompt):
        self.__println = println
        self.__prompt = prompt

    def missing_host_key(self, client, hostname, key):
        """missing_host_key [summary]

        Throws an exception if the key is not accepted

        Args:
            client (): -
            hostname (str): hostname of the connection which is to be established
            key (str): key of the server to which the connection is to be established
        """
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
