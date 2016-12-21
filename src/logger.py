import syslog


class Logger(object):
    def __init__(self, config):
        if config["DESTINATION"] == "CONSOLE":
            logger = ConsoleLogger()
        else:
            logger = SyslogLogger()

        self.logger = logger
        self.config = config
        self.logger.log("Creating logger: {0}.".format(type(self.logger)))

    def log(self, message):
        self.logger.log(message)


class ConsoleLogger(object):
    def log(self, message):
        print(message)


class SyslogLogger(object):
    def log(self, message):
        syslog.syslog(self.config["LEVEL"], "{0}\n".format(message))
