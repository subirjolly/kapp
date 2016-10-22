import socket
import select
import errno

class Listener(object):
    def __init__(self, host="0.0.0.0", port=1430):
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.bind((host, port))

    def start(self):
        self.sock.listen(1)
        connection, addr = self.sock.accept()
        print(str(addr))
        while True:
            data = self.read(connection)
            connection.send(data.upper())
            print(".")

        connection.close()

    def read(self, connection):
        BUFFER_SIZE = 1024
        response = []

        connection.setblocking(0)

        try:
            receiving = select.select([connection], [], [])
            while receiving:
                received = connection.recv(BUFFER_SIZE)
                if not received:
                    break
                response.append(received)
        except socket.error as e:
            if e.args[0] != errno.EWOULDBLOCK:
                raise e

        return "".join(response)
