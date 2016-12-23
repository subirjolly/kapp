class ClientDisconnectedError(Exception):
    MESSAGE = "Client disconnected from the server!"

    def __init__(self):
        super(ClientDisconnectedError, self).__init__(self.MESSAGE)

class NoProxyMatchError(Exception):
    MESSAGE = "No match found for command!"

    def __init__(self):
        super(NoProxyMatchError, self).__init__(self.MESSAGE)


class InvalidCommandError(Exception):
    MESSAGE = "Invalid command supplied!"

    def __init__(self):
        super(InvalidCommandError, self).__init__(self.MESSAGE)
