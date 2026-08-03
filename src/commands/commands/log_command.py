import os
from argparse import _SubParsersAction
from pathlib import Path

from colorama import Style, init

from commands.base.base_command import DEEP_PURPLE, BaseCommand, CLIOutput

init(autoreset=True)

messages = {

}


class LogCommand(BaseCommand):
    _name = "log"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers the log command parser with available arguments and flags.

        Args:
            registry: Subparser action manager where the command will be registered.
        """
        subparser = registry.add_parser(cls._name)
        subparser.add_argument(
            "-l",
            "--limit",
            type=int,
            default=-1,
            help="Maximum number of the newest commits to log. Defaults to -1, which means no limits.",
        )

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo, args) -> None:
        """Executes the log command to display history of commits.

        Args:
            repo: Repository instance on which the command will be executed.
            args: Parsed command-line arguments containing options.
        """
        limit: int = args.limit
        ignore_limit = True if limit < 0 else False
        branch_name = None

        if repo.read_head().split(" ", 1)[0] == "ref:":
            branch_name = Path(repo.read_head().split(" ", 1)[1]).name
            newest_commit_hash = repo.read_branch(branch_name)

        else:
            newest_commit_hash = repo.read_head()

        current_commit = repo.read_object(newest_commit_hash).decode("utf-8")
        print(current_commit)

