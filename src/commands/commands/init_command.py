import os
from argparse import _SubParsersAction
from pathlib import Path

from commands.base.base_command import BaseCommand


class InitCommand(BaseCommand):
    _name = "init"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers the init command parser with available arguments and flags.

        Args:
            registry: Subparser action manager where the command will be registered.
        """
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
        """Executes the init command to initialize a new repository.

        Args:
            repo: Repository instance on which the command will be executed.
            args: Parsed command-line arguments containing options like path and branch.
        """
        target_path: Path = args.path.resolve()

        target_path.mkdir(parents=True, exist_ok=True)
        os.chdir(target_path)
        repo.repo_path = target_path
        repo.initialize_directories()
        repo.update_head_path(args.branch_name)
