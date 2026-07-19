from src.commands.base.base_command import BaseCommand
import argparse
from argparse import _SubParsersAction


class ExampleCommand(BaseCommand):
    _name = "example"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        subparser = registry.add_parser(cls._name)
        subparser.add_argument("test_arg", type=str)

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo, args) -> None:
        print(repo)

        if hasattr(args, 'test_arg') and args.test_arg == "y":
            print("args_worken!")
        else:
            print("nuh uh")
            print(args)
