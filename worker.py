from client import Client

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
        self.connection = Client(self.host, self.port)
        self.connection.connect()
        return self.connection.read()

    def disconnect(self):
        self.connection.close()

    def run(self, command):
        if command.strip().lower() == "bye" or \
           command.strip().lower() == "logout":
            self.connection.close()
            return ""

        return self.connection.query(command)
