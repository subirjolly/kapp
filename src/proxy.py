import re
import uuid
from random import randint
from time import sleep

import socket
import select
import errno
import hashlib

from src.client import Client
from src.errors import ClientDisconnectedError, NoProxyMatchError


class Proxy(object):
    PATTERN = "^\S\slogin\s\S*\s\S*"
    END_PATTERN = "^\S\slogout*"

    def __init__(self):
        self.id = None

    def set_id(self, id):
        self.id = id

    def is_end(self, line):
        raise NotImplemented("match_ending method not implemented!")


class IMAPProxy(Proxy):
    HOST = "secure.emailsrvr.com"
    PORT = 143
    def __init__(self, line):
        parts = line.split()
        self.username = parts[2]
        self.password = parts[3]
        self.client = Client()

    def connect(self):
        return self.client.connect(self.HOST, self.PORT)

    def login(self, line):
        return self.client.query(line)

    def query(self, line):
        return self.client.query(line)


class ProxyGenerator(object):
    def __init__(self):
        self.proxies = {}

    def register(self, pattern, proxy_type):
        self.proxies[proxy_type] = pattern

    def generate(self, line):
        for proxy_type, pattern in self.proxies.items():
            # TODO: Pick up from here.
            # Need to generate proxy, then generate id and then run commands, then end.
            if re.match(pattern, line):
                return proxy_type(line)

        raise NoProxyMatchError()


class ProxyListener(object):
    def __init__(self, proxy_generator, data_store, connection, addr, logger):
        self.id = uuid.uuid4()
        self.proxy = None
        self.proxy_generator = proxy_generator
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
        try:
            self.data_store.clients_increment()
            self.logger.log("Starting proxy: {0}".format(self.id))
            self.logger.log("Used Proxies: {0}.".format(self.data_store.clients_count()))
            data = self.read()
            proxy = self.proxy_generator.generate(data)
            response = proxy.connect()
            
            response += proxy.login(data)

            while True:
                self.validate_connection()

                if response is None:
                    break
                self.connection.sendall(response.encode("UTF-8"))

                response = proxy.query(self.read())
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
