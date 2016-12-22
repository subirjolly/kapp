from client import Client

c = Client("127.0.0.1", 1430)
c.connect()
while True:
    inp = raw_input("Q: ")
    print("A: " + c.query(inp))
