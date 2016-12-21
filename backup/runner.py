from sys import stdin
from worker import Worker, WorkerConfig
from broker import Broker
from listener import Listener

#username = ""
#password = ""
#worker = Worker(username, password)
#print(worker.connect())
#commands = [
#    ". login ",
#    ". select inbox"
#]
#print(worker.run(". login {0} {1}".format(username, password)))
#print(worker.run(". SELECT INBOX"))

listener = Listener()
host = ""
port = 143

worker_config = WorkerConfig(host, port)
broker = Broker(listener=listener, worker_config=worker_config)
#TODO: Run this instead
broker.start()

username = ""
password = ""
#TODO: Remove this. This will be used by listen
broker.proxy(username, password)
broker.proxy(username, password)
