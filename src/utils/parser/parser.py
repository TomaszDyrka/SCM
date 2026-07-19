import argparse


class BaseParser:
    """
    """

    def __init__(self):
        self.main_parser = argparse.ArgumentParser(prog="rvn")
        self.subparser_registry = self.main_parser.add_subparsers(description="subcommands", dest="command")