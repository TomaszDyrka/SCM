import os
from argparse import _SubParsersAction
from pathlib import Path

from colorama import Style, init

from commands.base.base_command import DEEP_PURPLE, BaseCommand, CLIOutput

init(autoreset=True)

# messages = {
#     "success": lambda path, branch_name: (
#         f"Successfully initialized RVN repository at {DEEP_PURPLE}{path}{Style.RESET_ALL} "
#         f"with {DEEP_PURPLE}{branch_name}{Style.RESET_ALL} as its main branch."
#     )
# }


class CommitCommand(BaseCommand):
    _name = "commit"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers the init command parser with available arguments and flags.

        Args:
            registry: Subparser action manager where the command will be registered.
        """
        subparser = registry.add_parser(cls._name)
        subparser.add_argument(
            "message",
            type=str,
            help="Commit message.",
        )

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo, args) -> None:
        """Executes the commit command.

        Args:
            repo: Repository instance on which the command will be executed.
            args: Parsed command-line arguments containing options.
        """
        pass
