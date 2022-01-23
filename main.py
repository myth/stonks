from argparse import ArgumentParser
from logging import DEBUG, INFO, basicConfig, getLogger

from stonks import __version__, config
from stonks.app import Stonks


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", help="use a JSON config file to load positions")
    parser.add_argument("--db", help="path to SQLite databse file")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug output")
    parser.add_argument("-s", "--simulate", action="store_true", help="activate the simulation engine")
    parser.add_argument("-v", "--version", action="version", version=f"Stonks v{__version__}")
    args = parser.parse_args()

    log_level = DEBUG if args.debug else config.LOG_LEVEL
    basicConfig(level=log_level, format=config.LOG_FORMAT, datefmt=config.LOG_DATEFORMAT)
    getLogger("aiosqlite").setLevel(INFO)

    s = Stonks(args)
    s.run()
