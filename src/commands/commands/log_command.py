import os
import re
from argparse import _SubParsersAction
from datetime import datetime
from pathlib import Path

from colorama import Style, init

from commands.base.base_command import DEEP_PURPLE, BaseCommand, CLIOutput, DEEP_RED

init(autoreset=True)

messages = {
    "log_header": lambda commit_hash, branch_name: f"Commit {DEEP_RED}{commit_hash}{Style.RESET_ALL}" + f" on branch {DEEP_RED}{branch_name}{Style.RESET_ALL}" if branch_name is not None else "",
    "log_content": lambda author, date, message:
        f"Author: {DEEP_PURPLE}{author}{Style.RESET_ALL}\n"
        f"Commited on {DEEP_PURPLE}{date}{Style.RESET_ALL}\n"
        f"\n\t{message}\n"
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
        while True:

            CLIOutput.info(messages["log_header"](newest_commit_hash, branch_name))
            CLIOutput.blank(messages["log_content"](*LogCommand.parse_commit_info(current_commit)))

            parent_hash = LogCommand.parse_parent_hash(current_commit)
            if not ignore_limit:
                limit -= 1

            if not ignore_limit and limit <= 0:
                break

            if not parent_hash:
                break

            current_commit = repo.read_object(parent_hash).decode("utf-8")

    @staticmethod
    def parse_commit_info(text: str) -> tuple[str, str, str]:
        author_match = re.search(r"^author\s+(.*?)\s+(\d+)\s+([+-]\d{4})$", text, re.MULTILINE)

        author = ""
        formatted_date = ""

        if author_match:
            author = author_match.group(1)
            seconds = int(author_match.group(2))

            dt = datetime.fromtimestamp(seconds)
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")

        parts = text.split("\n\n", 1)
        message = parts[1].strip() if len(parts) > 1 else ""

        return author, formatted_date, message

    @staticmethod
    def parse_parent_hash(text: str) -> str:
        parent_match = re.search(r"^parent\s+([a-fA-F0-9]+)$", text, re.MULTILINE)
        return parent_match.group(1) if parent_match else ""
