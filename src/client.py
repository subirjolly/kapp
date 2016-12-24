import socket
import errno
import select

from src.errors import ClientDisconnectedError, InvalidCommandError

class Client(object):
    def __init__(self):
        self.host = None
        self.port = None
        self.block = None
        self.timeout = None
        self.connection = None
        self.addr = None

    def set_connection(self, connection, addr):
        self.connection = connection
        self.addr = addr

    def connect(self, host, port=143):
        self.host = host
        self.port = port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.port))

        return self.read()

    def close(self):
        self.connection.close()
        self.connection = None

    def validate(self):
        if self.connection is None:
            raise InvalidConnectionError()

        self.validate_connection()

    def validate_connection(self):
        received, _, _ = select.select([self.connection], [], [], 0)
        if received:
            peeked = self.connection.recv(1024, socket.MSG_PEEK)
            if len(peeked) == 0:
                raise ClientDisconnectedError()

    def query(self, command):
        self.validate()

        # HACK: Python client is ignoring if sending empty data.
        if command == "":
            raise InvalidCommandError()

        if command[-2:] != "\r\n":
            command += "\r\n"
        sent = self.connection.sendall(command.encode("UTF-8"))
        if sent == 0:
            self.close()

            raise InvalidConnectionError()

        return self.read()

    def read(self):
        self.validate()

        BUFFER_SIZE = 1024
        response = []

        self.connection.setblocking(0)

        try:
            receiving, _, _ = select.select([self.connection], [], [])

            while receiving:
                received = self.connection.recv(BUFFER_SIZE)

                if not received:
                    break

                response.append(received.decode("UTF-8"))
        except socket.error as e:
            if e.args[0] != errno.EWOULDBLOCK:
                raise e

        return "".join(response)


class InvalidConnectionError(Exception):
    pass
