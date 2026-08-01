import os
from argparse import _SubParsersAction
from pathlib import Path

from commands.base.base_command import BaseCommand


class AddCommand(BaseCommand):
    _name = "add"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers the add command parser with available arguments and flags.

        Args:
            registry: Subparser action manager where the command will be registered.
        """
        subparser = registry.add_parser(cls._name)
        # subparser.add_argument(
        #     "-p",
        #     "--path",
        #     type=Path,
        #     default=Path.cwd(),
        #     help="Path where .rvn directory will be created (current directory by default).",
        # )

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo, args) -> None:
        """Executes the add command.

        Args:
            repo: Repository instance on which the command will be executed.
            args: Parsed command-line arguments containing options
        """
        pass
