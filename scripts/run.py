from src.kapp import KAPP
from src.logger import Logger
from src.config.loader import ConfigLoader
from src.proxy import SampleProxy, ProxyGenerator


def main():
    print("Starting kapp..")
    loader = ConfigLoader("default.cfg")
    logger = Logger(loader.get("LOGGER"))
    kapp = KAPP(loader.get("KAPP"), logger)

    generator = ProxyGenerator()
    generator.register(SampleProxy.PATTERN, SampleProxy)
    generator.generate(". login abc def")

    proxy = SampleProxy()
    kapp.start(proxy)

if __name__ == "__main__":
    main()
