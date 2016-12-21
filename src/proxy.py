import uuid
from random import randint
from time import sleep

import socket
import select
import errno
import hashlib

class Proxy(object):
    def __init__(self, data_store, logger):
        self.id = uuid.uuid4()
        self.data_store = data_store
        self.logger = logger
        self.logger.log("Spawning: {0}".format(self.id))

    def start(self):
        self.data_store.clients_increment()
        self.logger.log("Starting proxy: {0}".format(self.id))
        for i in range(randint(1, 4)):
            self.logger.log("Process: {0}. Sleeping({1}).".format(self.id, i))
            #sleep(1)
        self.logger.log("Decrementing proxy: {0}".format(self.id))
        self.data_store.clients_decrement()

        # TODO: Inject this instead.
        self.logger.log("Connecting")
        try:
            listener = ProxyListener("127.0.0.1", 1430)
        except Exception as e:
            raise
        self.logger.log("Decremented")
        self.logger.log("Listening proxy: {0}".format(self.id))
        listener.start()


class ProxyListener(object):
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.sock.bind((host, port))

        self.pool = {}

    def _get_digest(self, username, password):
        h = hashlib.new('sha256')
        h.update("{0}:{1}".format(
            username, password))

        return h.hexdigest()


    def start(self):
        self.sock.listen(1)
        connection, addr = self.sock.accept()
        worker = None
        try:
            while True:
                data = self.read(connection)
                try:
                    if "quit" in data:
                        break

                    if data:
                        connection.sendall(data.encode("UTF-8"))
                except Exception as e:
                    pass
        finally:
            connection.close()

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
                response.append(received.decode("UTF-8"))
        except socket.error as e:
            if e.args[0] != errno.EWOULDBLOCK:
                raise e
        result = "".join(response)

        return result
