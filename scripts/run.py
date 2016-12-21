from src.kapp import KAPP
from src.logger import Logger
from src.config.loader import ConfigLoader


def main():
    print("Starting kapp..")
    loader = ConfigLoader("default.cfg")
    logger = Logger(loader.get("LOGGER"))
    kapp = KAPP(loader.get("KAPP"), logger)
    kapp.start()

if __name__ == "__main__":
    main()
