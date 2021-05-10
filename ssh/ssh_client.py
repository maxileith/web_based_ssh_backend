import json
import os
import socket
import re
from paramiko.py3compat import u
from time import sleep
import queue
from io import StringIO
import paramiko
from web_based_ssh_backend.settings import KNOWN_HOSTS_DIRECTORY, DEBUG


def is_private_host(hostname):
    """is_private_host [summary]

    Checks if the given Domain/IP resolves/is to a private IPv4/v6

    Args:
        hostname (String): Domain/IP to check

    Returns:
        Boolean: True if the given hostname resolves to a private IP
    """
    if DEBUG:
        return False
    # private pattern
    pattern4 = '(^127\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)|(^169\.254\.)'
    pattern6 = '(^::1$)|(^[fF][cCdD])'
    # check if ipv6 is private
    try:
        ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]
        if re.match(pattern6, ipv6):
            return True
    except socket.gaierror:
        pass
    # check if ipv4 is private
    try:
        ipv4 = socket.getaddrinfo(hostname, None)[0][4][0]
        if re.match(pattern4, ipv4):
            return True
    except socket.gaierror:
        pass

    return False


class SSHClientController:

    # how often the output of the SSH Client ist checked
    FPS = 30
    INTERVAL = 1.0/FPS
    # Timeout of the SSH Client (seconds)
    TIMEOUT = 15

    def __init__(self, consumer, user_id: int, hostname: str = None, username: str = None, password: str = None, port:  int = 22, rsa_path: str = None, known_host:  str = None):
        """__init__ [summary]

        Create a controller and give it all the information needed for the connection.

        Args:
            consumer (SSHConsumer): Consumer to send the output to.
            user_id (int): ID of the user that tries want to connect.
            hostname (str, optional): Hostname to which the connection is to be established. Defaults to None.
            username (str, optional): Username used to authenticate to the server. Defaults to None.
            password (str, optional): Password used to authenticate to the server. Defaults to None.
            port (int, optional): Port to which the connection is to be established. Defaults to 22.
            rsa_path (str, optional): Path to the rsa keyfile used to authenticate to the server. Defaults to None.
        """
        self.consumer = consumer
        self.user_id = user_id
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.rsa_path = rsa_path
        self.known_host = known_host
        self.input_queue = queue.Queue()
        self.running = True

    def run(self):
        """run [summary]

        main programme logic
        this method has to be called to start the SSH Client

        """
        # prevent connection to private hosts
        if is_private_host(self.hostname):
            self.__println("private hosts are not allowed")
            self.consumer.close()
            return

        # new paramiko client
        self.client = paramiko.SSHClient()

        # set custom host key policy
        key_policy = HostKeyChecker(
            self.__println, self.__prompt, self.known_host)
        self.client.set_missing_host_key_policy(policy=key_policy)

        # try to connect and quit if it fails
        if not self.__connect():
            self.consumer.close()
            return

        # start the interactive shell
        self.__interactive_shell()

        # close client and the consumer that started the thread
        self.client.close()
        self.consumer.close()

    def input(self, x: str):
        """input [summary]

        Method to send data to the client.

        Args:
            x (str): String to be passed on to the client.
        """
        self.input_queue.put(x)

    def stop(self):
        """stop [summary]

        Stops the main loop

        """
        self.running = False

    def __print(self, txt: str):
        """__print [summary]

        Print to consumer.

        Args:
            txt (str): Text to be printed.
        """
        self.__send(u(str(txt)))

    def __println(self, txt: str):
        """__println [summary]

        Analogous to __print, with newline at the end.

        Args:
            txt (str): Text to be printed.
        """
        self.__print(txt)
        self.__send(u('\r\n'))

    def __prompt(self, prompt: str = ''):
        """__prompt [summary]

        Prompts the user to do something.

        Args:
            prompt (str, optional): Prompt text. Defaults to ''.

        Returns:
            str: Response from user
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
                # send output to consumer
                while channel.recv_ready():
                    # raw data to unicode
                    r = u(channel.recv(1024))
                    # EOF - End of File
                    if len(r) == 0:
                        return
                    self.__send(r)

                # flush input queue by sending the data
                while channel.send_ready() and not self.input_queue.empty():
                    channel.send(u(self.input_queue.get()))

        __loop_tasks()

    def __send(self, x: str):
        """__send [summary]

        Sends data to the user.

        Args:
            x (str): data to be send
        """
        self.consumer.send(text_data=json.dumps({
            'data': x
        }))


class HostKeyChecker(paramiko.MissingHostKeyPolicy):
    def __init__(self, println, prompt, path):
        self.__println = println
        self.__prompt = prompt
        self.__path = path

    def missing_host_key(self, client, hostname, key):
        """missing_host_key [summary]

        - Throws an exception if the key is not accepted
        - Asks if the user wants to add the key
        - Asks if the user wants to updated the key

        Args:
            client (): -
            hostname (str): hostname of the connection which is to be established
            key (str): key of the server to which the connection is to be established
        """
        # load and return known host keys
        known_host_keys = paramiko.util.load_host_keys(self.__path)
        # check if key is known, changed or unknown
        case = self.__identify_case(hostname, known_host_keys, key)
        # ask the user what to do if needed
        if case == "unknown":
            self.__handle_unknown(hostname, known_host_keys, key)
        elif case == "changed":
            self.__handle_changed(hostname, known_host_keys, key)

    def __identify_case(self, hostname, known_host_keys, key):
        """__identify_case [summary]

        Identifies if the host key to check is known, unknown or has changed

        Args:
            hostname (String): Hostname
            known_host_keys ([type]): Known host Keys
            key ([type]): host key to check

        Returns:
            "unknown" | "changed" | "known": returns if the host key to check is known,
                                             unknown or has changed
        """
        if hostname not in known_host_keys or key.get_name() not in known_host_keys[hostname]:
            # host key is new
            return "unknown"
        if known_host_keys[hostname][key.get_name()] != key:
            # host key of the host changed
            return "changed"
        # host key is known
        return "known"

    def __handle_unknown(self, hostname, known_host_keys, key):
        """__handle_unknown [summary]

        - print warning with the key to check
        - ask if the key is alright
        - add the key to known hosts if the user accepts the key
        - raise HostKeyError if the user declines the key

        Args:
            hostname (String): hostname
            known_host_keys: known hosts
            key (String): new key

        Raises:
            HostKeyError: [description]
        """
        # warning
        self.__println(
            f'*** WARNING: Unknown host key: {key.get_base64()}')

        # ask the user if he / she wants to add the key
        add = self.__prompt(
            "Add the host key to known hosts? (y/N): ")
        if add.capitalize() == 'Y':
            known_host_keys.add(hostname=hostname,
                                keytype='ssh-rsa', key=key)
            known_host_keys.save(self.__path)
            self.__println(
                '*** INFO: Added host key to known hosts!')
            return

        raise HostKeyError

    def __handle_changed(self, hostname, known_host_keys, key):
        """__handle_changed [summary]

        - print warning with the old key and the key to check
        - ask if the new key is alright
        - update the key in the known hosts file if the user accepts the new key
        - raise HostKeyError if the user declines the new key 

        Args:
            hostname (String): hostname
            known_host_keys: known hosts
            key (String): new key

        Raises:
            HostKeyError: [description]
        """
        # warning
        self.__println('*** WARNING: Host key has changed!')
        self.__println(
            f'*** Old Key: {known_host_keys[hostname][key.get_name()].get_base64()}')
        self.__println(f'*** New Key: {key.get_base64()}')

        # ask the user if he / she wants to update the key
        update = self.__prompt('Update the host key? (y/N): ')
        if update.capitalize() == 'Y':
            # delete old key
            del known_host_keys[hostname]
            # add new key
            known_host_keys.add(hostname=hostname, keytype='ssh-rsa', key=key)
            known_host_keys.save(self.__path)
            self.__println('*** Info: Host key updated!')
            return

        raise HostKeyError


class HostKeyError(Exception):
    """HostKeyError [summary]

    just a generic Exception to use if a host key is not valid

    """
    pass
