import socket

from multiprocessing import Process, Lock, Queue, Pool
from multiprocessing.managers import BaseManager, BaseProxy

from src.proxy import ProxyListener
from src.logger import Logger


class DataStore(object):
    def __init__(self):
        self.lock = Lock()
        self.count = 0
        self.clients = {}

    def clients_increment(self):
        self.lock.acquire()
        self.count += 1
        self.lock.release()

    def clients_decrement(self):
        self.lock.acquire()
        self.count -= 1
        self.lock.release()

    def clients_count(self):
        return self.count

    def set_client(self, cid, client):
        self.clients[cid] = client


class KAPPManager(BaseManager):
    pass


class KAPP(object):
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self.logger.log("Starting engine!")
        KAPPManager.register("DataStore", DataStore)
        self.manager = KAPPManager()
        self.sock = None

    def start(self, proxy_generator):
        count = int(self.config["PROCESSES"])
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 1430))
        self.sock.listen(count)

        self.manager.start()
        data_store = self.manager.DataStore()
        pool = Pool(count)

        while True:
            if data_store.clients_count() >= count:
                continue

            self.logger.log("Used: {0}.".format(data_store.clients_count()))
            connection, addr = self.sock.accept()

            pool.apply_async(func=spin_up, args=(proxy_generator, connection, addr, data_store, self.logger))

        pool.close()


def spin_up(proxy_generator, connection, addr, data_store, logger):
    logger.log("Starting proxy!")
    listener = ProxyListener(proxy_generator, data_store, connection, addr, logger)
    try:
        listener.start()
    except Exception as e:
        logger.log(str(e))
        raise
