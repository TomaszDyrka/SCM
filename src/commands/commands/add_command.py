import os
from argparse import _SubParsersAction
from pathlib import Path
from colorama import Style, init
from commands.base.base_command import BaseCommand, CLIOutput, DEEP_PURPLE, DEEP_RED
from models.binary_large_object import BinaryLargeObject
from repository.find_root import find_repository_root

IGNORED_DIRS = {
    ".rvn",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
}

init(autoreset=True)

class AddCommand(BaseCommand):
    _name = "add"
    _messages = {
        "added_file": lambda path: (
            f"Added file {DEEP_PURPLE}{path}{Style.RESET_ALL}"
        ),
        "not_found": lambda path: (
            f"There's no file or directory of path {DEEP_RED}{path}{Style.RESET_ALL}"
        ),
    }

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
            CLIOutput.error(AddCommand._messages["not_found"](target_path))

    @staticmethod
    def add_file(repo, args) -> None:
        file_path = args.path

        # Read file's bytes and create BLOB object
        file_bytes = file_path.read_bytes()
        file_blob = BinaryLargeObject(file_bytes)

        # Save BLOB in .rvn/objects
        repo.set_repository_path(find_repository_root().parent)
        repo.write_object(file_blob.serialize())

        # Add file to the staging area
        repo.add_file_to_index(file_path, file_blob)
        CLIOutput.info(AddCommand._messages["added_file"](file_path))

    @staticmethod
    def add_directory(repo, args) -> None:
        directory_path = args.path
        repo_root = find_repository_root().parent
        repo.set_repository_path(repo_root)

        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                # Skip files inside .rvn directory
                if any(part in IGNORED_DIRS for part in file_path.parts):
                    continue

                # Read file's bytes and create BLOB object
                file_bytes = file_path.read_bytes()
                file_blob = BinaryLargeObject(file_bytes)

                # Add file to the staging area
                repo.write_object(file_blob.serialize())
                repo.add_file_to_index(file_path, file_blob)
                CLIOutput.info(AddCommand._messages["added_file"](file_path))
