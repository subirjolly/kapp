import socket
import select
import errno
import hashlib

from multiprocessing import Process
from worker import Worker

class Broker(object):
    def __init__(self, host, port, worker_config):
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.bind((host, port))

        self.pool = {}
        self.worker_config = worker_config

    def _get_digest(self, username, password):
        h = hashlib.new('sha256')
        h.update("{0}:{1}".format(
            username, password))

        return h.hexdigest()

    def _get_worker(self, username, password):
        digest = self._get_digest(username, password)
        if digest not in self.pool:
            worker = Worker(self.worker_config)
            self.pool[digest] = worker
            print("New worker")
        else:
            worker = self.pool[digest]
            print("Found worker")

        return worker

    def start(self):
        self.sock.listen(1)
        connection, addr = self.sock.accept()
        print("Connection from: {0}.".format(str(addr)))
        worker = None
        while True:
            data = self.read(connection)
            print(data)
            result = ""
            try:
                if "login" in data:
                    username, password = self._parse_credentials(data)
                    worker = self._get_worker(username, password)
                    if worker.is_connected() is not True:
                        result = worker.connect()

                if worker and data:
                    print("DATA: .{0}.".format(data))
                    result += worker.query(data)
                    print("Sending back: {0}".format(result))
                    connection.sendall(result)
            except:
                pass

        connection.close()

    def _parse_credentials(self, data):
        parts = data.split(" ")
        if len(parts) < 4:
            raise Exception("Invalid login command!")

        return parts[2], parts[3]

    def read(self, connection):
        BUFFER_SIZE = 1024
        response = []

        connection.setblocking(0)

        try:
            receiving, _, _ = select.select([connection], [], [])
            while receiving:
                received = connection.recv(BUFFER_SIZE)
                if not received:
                    break
                response.append(received)
        except socket.error as e:
            if e.args[0] != errno.EWOULDBLOCK:
                raise e

        return "".join(response)
