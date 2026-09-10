from argparse import _SubParsersAction
from pathlib import Path

from colorama import init

from commands.base.base_command import BaseCommand
from models.commit import Commit
from models.tree import Tree
from repository.repository import Repository, get_file_mode
from errors.errors import BranchAlreadyExistsError, RepositoryNotInitializedError

init(autoreset=True)

messages = {
    "branch_created": lambda name, commit_hash: (
        f"Created branch {DEEP_PURPLE}{name}{Style.RESET_ALL} at commit {DEEP_RED}{commit_hash[:7]}{Style.RESET_ALL}."
    ),
    "branch_exists": lambda name: (
        f"Branch {DEEP_RED}{name}{Style.RESET_ALL} already exists."
    ),
    "repo_not_initialized": f"Repository has not been initialized yet. Use {DEEP_RED}rvn init{Style.RESET_ALL} and try again.",
}

class BranchCommand(BaseCommand):
    _name = "branch"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers parser with branch command.
        Args:
            registry: main parser of the scm
        """
        subparser = registry.add_parser(cls._name)
        subparser.add_argument(
            "name",
            type=str,
            help="Branch name",
        )

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo: Repository, args) -> None:
        """Creates a new branch
        Args:
            repo: repository on which command will be executed
            args: parsed command-line arguments containing options
        """
        try:
            with repo.HEAD.open() as head:
                content = head.readline().split()
                # if content is a reference (ref: refs/heads/...)
                if len(content) > 1:
                    commit_hash = (repo.repository_path / Path(content[1])).read_text()
                # if content is directly a hash
                else:
                    commit_hash = content[0]
                
            path = repo.refs / "heads" / args.name
            
            if not path.is_file():
                with open(file=path, mode="w") as head_file:
                    head_file.write(commit_hash)
                    
                CLIOutput.info(messages["branch_created"](args.name, commit_hash))
                return
                
            # if branch exists already - Error
            raise BranchAlreadyExistsError
            
        except RepositoryNotInitializedError:
            CLIOutput.error(messages["repo_not_initialized"])
        except FileNotFoundError:
            CLIOutput.error(messages["repo_not_initialized"])
        except BranchAlreadyExistsError:
            CLIOutput.error(messages["branch_exists"](args.name))
