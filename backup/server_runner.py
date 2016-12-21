from broker import Broker
from worker import WorkerConfig

host = "secure.emailsrvr.com"
port = 143

worker_config = WorkerConfig(host, port)
Broker("localhost", 1430, worker_config).start()
