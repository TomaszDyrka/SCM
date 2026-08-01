import os
from argparse import _SubParsersAction
from pathlib import Path

from commands.base.base_command import BaseCommand
from models.binary_large_object import BinaryLargeObject


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
            nargs="?",
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

        target_path: Path = args.path

        if target_path.is_file():
            AddCommand.add_file(repo, args)

        elif target_path.is_dir():
            AddCommand.add_directory(repo, args)

        else:
            print(f"There's no file or directory of path {target_path}")

    @staticmethod
    def add_file(repo, args) -> None:
        file_path = args.path

        # Read file's bytes and create BLOB object
        file_bytes = file_path.read_bytes()
        file_blob = BinaryLargeObject(file_bytes)

        # Save BLOB in .rvn/objects
        blob_hash = repo.write_object(file_blob.serialize())

    @staticmethod
    def add_directory(repo, args) -> None:
        pass
