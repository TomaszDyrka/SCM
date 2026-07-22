from commands.base.base_command import BaseCommand
import argparse
from argparse import _SubParsersAction


class ExampleCommand(BaseCommand):
    _name = "example"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        subparser = registry.add_parser(cls._name)
        subparser.add_argument("test_pos_arg", type=str, help="important arg, pass y so you can view different message!")
        subparser.add_argument("-o", "--test_opt_arg", type=int, help="you can pass the 5 to see if it is woooorking!")

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo, args) -> None:
        print(repo)

        if hasattr(args, 'test_pos_arg') and args.test_pos_arg == "y":
            print("args_worken!")
        else:
            print("nuh uh")
            print(args)

        if hasattr(args, 'test_opt_arg') and args.test_opt_arg == 5:
            print("opt arg is woooorking!")