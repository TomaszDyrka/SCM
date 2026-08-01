import argparse


class BaseParser:
    """Base class for initializing Parser object"""

    def __init__(self):
        self.main_parser = argparse.ArgumentParser(prog="rvn")
        self.subparser_registry = self.main_parser.add_subparsers(
            description="subcommands", dest="command"
        )
