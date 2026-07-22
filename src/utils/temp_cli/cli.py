import argparse
import inspect

from repository import repository as rp

from commands.commands import *
import commands.commands as cmd_pkg

from utils.parser.parser import BaseParser
from commands.base.base_command import BaseCommand


def setup_cli() -> BaseParser:
    parser = BaseParser()

    # we iterate over every command file, importing the module it represents
    for command_file in cmd_pkg.__all__:
        module = globals()[command_file]

        # now we select classes (so commands in this case) and...
        for name, obj in inspect.getmembers(module, inspect.isclass):

            # ...if they are inherited from BaseCommand, we register
            # them in registry
            if issubclass(obj, BaseCommand) and obj is not BaseCommand:
                obj.register_parser(parser.subparser_registry)
                print(f"Registered command: {obj._name}")

    return parser
