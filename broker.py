import hashlib
from multiprocessing import Process
from worker import Worker


class Broker(object):
    def __init__(self, listener, worker_config):
        self.pool = {}
        self.listener = listener
        self.worker_config = worker_config

    def start(self):
        self.listener.start()

    def get_digest(self, username, password):
        h = hashlib.new('sha256')
        h.update("{0}:{1}".format(username, password))

        return h.hexdigest()

    def proxy(self, username, password):
        digest = self.get_digest(username, password)
        if digest not in self.pool:
            worker = Worker(self.worker_config)
            self.pool[digest] = worker
        else:
            worker = self.pool[digest]

        proc = Process(
            name="{0}: {1}".format(username, digest),
            target=run_worker,
            args=(worker, username, password))
        proc.start()
        proc.join()

    def listen(self):
        # TODO: Listen for client requests
        pass


# FIXME: Needs to respond back to client
def run_worker(worker, username, password):
    response = []
    commands = [
        ". login {0} {1}".format(username, password),
        ". select inbox"
    ]
    try:
        if worker.is_connected() is not True:
            response.append(worker.connect())

        for command in commands:
            result = worker.run(command)
            response.append(result)
    except Exception as e:
        print(str(e))
        pass

    print(response)
    return response
