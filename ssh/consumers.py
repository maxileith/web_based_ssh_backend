import json
from channels.generic.websocket import WebsocketConsumer
import threading

from saved_sessions.models import SSHSession
from known_hosts.models import KnownHost

from .ssh_client import SSHClientController


class SSHConsumer(WebsocketConsumer):
    """SSHConsumer [summary]

    Class that handles the websocket communication to make the SSH Client
    accessable to the users

    """

    def connect(self):
        """connect [summary]

        - Initial connect
        - Loads the corresponding session data
        - Makes sure the user that tries to access the session has the privileges
        - Loads the known hosts file path of the user
        - Creates the SSH Client
        - Starts the SSH Client in a dedicated thread

        """
        self.ssh_client = None

        # get session data
        ssh_session_id = self.scope['url_route']['kwargs']['ssh_session_id']
        self.user = self.scope['user']
        self.session_data = self.__get_session_data(self.user, ssh_session_id)

        # close connection if there is no session data
        if not self.session_data:
            self.close()
            return

        key_file = None
        if self.session_data.key_file:
            key_file = self.session_data.key_file.path

        # load known hosts file path of the user
        known_host = KnownHost.objects.get(user=self.user)

        # create a new SSH client
        self.ssh_client = SSHClientController(
            self, user_id=self.user.id, hostname=self.session_data.hostname,
            username=self.session_data.username, password=self.session_data.password,
            rsa_path=key_file, port=self.session_data.port, known_host=known_host.file.path)

        # everything seems fine --> accept connection
        self.accept()

        # start the ssh client in a dedicated thread
        self.thread = threading.Thread(target=self.ssh_client.run)
        self.thread.start()

    def receive(self, text_data):
        """receive [summary]

        forwards incoming text to the SSH Client

        Args:
            text_data (String): Text to send to the SSH Client
        """
        self.ssh_client.input(json.loads(text_data)["data"])

    def disconnect(self, close_code):
        """disconnect [summary]

        sends the stop signal to the SSH Client

        """
        if self.ssh_client:
            self.ssh_client.stop()

    def __get_session_data(self, user, session_id):
        """__get_session_data [summary]

        returns the session data of the specified session if the
        user is the owner of the session

        Args:
            user: the user that wants to access the session
            session_id (Integer): the identifier of the session

        Returns:
            Session: return a Session object or None if the session
                     does not exist or the user has no access to it
        """
        return SSHSession.objects.filter(user=user, id=session_id).first()
