from pathlib import Path
from commands.base.base_command import BaseCommand
import argparse
from argparse import _SubParsersAction

from repository.repository import Repository


class ExampleCommand(BaseCommand):
    _name = "init"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        subparser = registry.add_parser(cls._name)
        subparser.add_argument(
            "-p",
            "--path",
            type=Path,
            default=Path.cwd(),
            help="Path where .rvn directory will be created (current directory by default).",
        )
        subparser.add_argument(
            "-b",
            "--branch",
            dest="branch_name",
            type=str,
            default="master",
            help="Name of the initial branch ('master' by default).",
        )

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo, args) -> None:
        repo_path: Path = args.path
        branch_name: str = args.branch_name

        repository = Repository(repo_path)
        repository.initialize_directories()
        repository.update_head_path(branch_name)