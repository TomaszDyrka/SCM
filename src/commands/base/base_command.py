import abc
from argparse import _SubParsersAction

from repository.repository import Repository

DEEP_PURPLE = "\033[38;2;138;43;226m"
DEEP_RED = "\033[38;2;178;34;34m"


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
