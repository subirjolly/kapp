from multiprocessing import Process, Lock, Queue, Pool
from multiprocessing.managers import BaseManager, BaseProxy

from src.proxy import Proxy
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

    def start(self):
        count = int(self.config["PROCESSES"])
        self.manager.start()
        data_store = self.manager.DataStore()
        pool = Pool(count)

        while True:
            self.wait()

            is_available = False
            if data_store.clients_count() < count:
                pool.apply_async(func=spin_up, args=(data_store, self.logger))
            else:
                self.logger.log("Not spawning")

            self.logger.log("Used: {0}.".format(data_store.clients_count()))

        pool.close()

    def wait(self):
        data = input("> ")
        if data.lower() == "q":
            raise Exception()


def spin_up(data_store, logger):
    p = Proxy(data_store, logger)
    try:
        p.start()
    except Exception as e:
        print(str(e))
        raise
