from src.kapp import KAPP
from src.logger import Logger
from src.config.loader import ConfigLoader
from src.proxy import IMAPProxy, ProxyGenerator


def main():
    print("Starting kapp..")
    loader = ConfigLoader("default.cfg")
    logger = Logger(loader.get("LOGGER"))
    kapp = KAPP(loader.get("KAPP"), logger)

    generator = ProxyGenerator()
    generator.register(IMAPProxy.PATTERN, IMAPProxy)
    #proxy = generator.generate(". login abc def")
    #print(proxy.username)
    #print(proxy.password)
    #proxy = IMAPProxy(". login test1@dev.webmail.us Pr0d_web@pps_t3st")
    #while True:
    #    inp = input("Q: ")
    #    proxy.query(inp)


    kapp.start(generator)

if __name__ == "__main__":
    main()
