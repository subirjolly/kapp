import socket
import errno
import select


class Client(object):
    def __init__(self, host, port=143, block=0, timeout=0):
        self.host = host
        self.port = port
        self.block = block
        self.timeout = timeout
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.connection.connect((self.host, self.port))

    def close(self):
        self.connection.close()
        self.connection = None

    def validate(self):
        if self.connection is None:
            raise InvalidConnectionError()

    def query(self, command):
        self.validate()

        if command[-2:] != "\r\n":
            command += "\r\n"
        sent = self.connection.sendall(command.encode("utf-8"))
        if sent == 0:
            self.close()

            raise InvalidConnectionError()

        response = self.read()

        return response

    def read(self):
        self.validate()

        BUFFER_SIZE = 1024
        response = []

        self.connection.setblocking(self.block)
        if self.timeout > 0:
            self.connection.settimeout(self.timeout)

        try:
            receiving, _, _ = select.select([self.connection], [], [])
            while receiving and True:
                received = self.connection.recv(BUFFER_SIZE)
                if not received:
                    break
                response.append(received)
        except socket.error as e:
            if e.args[0] != errno.EWOULDBLOCK:
                raise e

        return "".join(response)


class InvalidConnectionError(Exception):
    pass
