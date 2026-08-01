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
        subparser.add_argument(
            "path",
            type=Path,
            default=Path("."),
            help="Path of a file/directory that is to be added to the staging area.",
        )

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo, args) -> None:
        """Executes the add command.

        Args:
            repo: Repository instance on which the command will be executed.
            args: Parsed command-line arguments containing options
        """
        pass

    @staticmethod
    def add_file(repo, args) -> None:
        pass

    @staticmethod
    def add_directory(repo, args) -> None:
        pass
