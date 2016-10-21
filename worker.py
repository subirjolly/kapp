import socket
import errno
import select


class InvalidConnectionError(Exception):
    pass


class WorkerConfig(object):
    def __init__(self, host="127.0.0.1", port=143):
        self.host = host
        self.port = port


class Worker(object):
    def __init__(self, config):
        self.host = config.host
        self.port = config.port
        self.connection = None

    def is_connected(self):
        return (self.connection is not None)

    def connect(self):
        self.connection = Connection(self.host, self.port)
        return self.connection.read()

    def disconnect(self):
        self.connection.close()

    def run(self, command):
        if command.strip().lower() == "bye" or \
           command.strip().lower() == "logout":
            self.connection.close()
            return ""

        return self.connection.query(command)


class Connection(object):
    def __init__(self, host, port=143):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host, port))

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
        sent = self.connection.send(command.encode("utf-8"))
        if sent == 0:
            self.close()

            raise InvalidConnectionError()

        response = self.read()

        return response

    def read(self):
        self.validate()

        BUFFER_SIZE = 1024
        response = []

        self.connection.setblocking(0)

        try:
            receiving = select.select([self.connection], [], [])
            while receiving:
                received = self.connection.recv(BUFFER_SIZE)
                if not received:
                    break
                response.append(received)
        except socket.error as e:
            if e.args[0] != errno.EWOULDBLOCK:
                raise e

        return "".join(response)
