import uuid
from random import randint
from time import sleep

import socket
import select
import errno
import hashlib

from src.errors import ClientDisconnectedError



class ProxyListener(object):
    def __init__(self, data_store, connection, addr, logger):
        self.id = uuid.uuid4()
        self.data_store = data_store
        self.logger = logger
        self.addr = addr
        self.connection = connection

    def _get_digest(self, username, password):
        h = hashlib.new('sha256')
        h.update("{0}:{1}".format(
            username, password))

        return h.hexdigest()

    def start(self):
        self.data_store.clients_increment()
        self.logger.log("Starting proxy: {0}".format(self.id))
        self.logger.log("Used Proxies: {0}.".format(self.data_store.clients_count()))

        try:
            while True:
                self.validate_connection()

                try:
                    data = self.read()
                    if data is None:
                        break

                    self.connection.sendall(data.encode("UTF-8"))
                except:
                    pass
        except ClientDisconnectedError:
            self.logger.log("Client disconnected for proxy: {0}.".format(self.id))
        finally:
            self.logger.log("Stopping proxy: {0}".format(self.id))
            self.data_store.clients_decrement()
            self.connection.close()

    def validate_connection(self):
        received, _, _ = select.select([self.connection], [], [], 0)
        if received:
            peeked = self.connection.recv(1024, socket.MSG_PEEK)
            if len(peeked) == 0:
                raise ClientDisconnectedError()

    def read(self):
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
