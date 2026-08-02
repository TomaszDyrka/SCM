import abc
from argparse import _SubParsersAction
from colorama import Style, init
from repository.repository import Repository

init(autoreset=True)

DEEP_PURPLE = "\033[38;2;138;43;226m"
DEEP_RED = "\033[38;2;178;34;34m"
DEEP_GRAY = "\033[38;2;105;105;105m"


class BaseCommand(abc.ABC):
    _name = "base"

    @classmethod
    @abc.abstractmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers parser with own commands
        Args:
            registry: main parser of the scm
        """

    @staticmethod
    @abc.abstractmethod
    def execute(repo: Repository, *args, **kwargs) -> None:
        """Executes the command on given repository with given flags and options
        Args:
            repo: repository on which command will be executed
            *args: listed arguments
            **kwargs: key-value arguments
        """

class CLIOutput:
    verbose: bool = True
    quiet: bool = False

    @classmethod
    def info(cls, message: str) -> None:
        if not cls.quiet:
            print(f"{DEEP_PURPLE}INFO:{Style.RESET_ALL} {message}")

    @classmethod
    def error(cls, message: str) -> None:
        print(f"{DEEP_RED}ERROR:{Style.RESET_ALL} {message}")

    @classmethod
    def debug(cls, message: str) -> None:
        if cls.verbose:
            print(f"{DEEP_GRAY}DEBUG:{Style.RESET_ALL} {message}")
