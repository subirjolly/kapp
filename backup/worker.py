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

    def query(self, command):
        parts = command.split(" ")
        if len(parts) > 1 and (
           parts[1].lower() == "logout" or \
           parts[1].lower() == "bye"):
            self.connection.close()
            return ""

        result = self.connection.query(command)
        return result
