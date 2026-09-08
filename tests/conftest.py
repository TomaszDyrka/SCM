from argparse import _SubParsersAction
from pathlib import Path

import pytest

from src.commands.base.base_command import BaseCommand
from src.models.binary_large_object import BinaryLargeObject
from src.models.commit import Commit
from src.models.tree import Tree
from src.repository.repository import Repository
from src.utils.parser.parser import BaseParser
from src.utils.temp_cli.cli import setup_cli


@pytest.fixture
def temp_repo(tmp_path: Path):
    return Repository(tmp_path)


@pytest.fixture
def temp_repo_initialized(tmp_path: Path):
    repo = Repository(tmp_path)
    repo.initialize_directories()
    return repo


@pytest.fixture
def create_blob():
    def _create_blob(content: bytes = b"default_content") -> BinaryLargeObject:
        return BinaryLargeObject(content)

    return _create_blob


@pytest.fixture
def create_commit():
    def _create_commit(
        tree: str = "default_tree_hash",
        parent_hashes: list[str] | None = None,
        author: str = "John Doe",
        committer: str = "John Doe",
        message: str = "Default commit message",
        timestamp: str = "1700000000",
    ) -> Commit:
        return Commit(
            tree=tree,
            parent_hashes=parent_hashes
            if parent_hashes is not None
            else ["default_parent_hash"],
            author=author,
            committer=committer,
            message=message,
            timestamp=timestamp,
        )

    return _create_commit


@pytest.fixture
def create_tree():
    def _create_tree(entries=None) -> Tree:
        tree = Tree()
        if entries:
            for entry in entries:
                tree.add_entry(
                    entry_hash=entry["hash"],
                    entry_type=entry["type"],
                    entry_name=entry["name"],
                )
        return tree

    return _create_tree


@pytest.fixture
def create_parser():
    def _create_parser() -> BaseParser:
        parser = setup_cli()
        return parser

    return _create_parser
    
@pytest.fixture
def example_command():
    class ExampleCommand(BaseCommand):
        _name = "example"

        @classmethod
        def register_parser(cls, registry: _SubParsersAction) -> None:
            subparser = registry.add_parser(cls._name)
            subparser.add_argument("test_pos_arg", type=str, help="important arg, pass y so you can view different message!")
            subparser.add_argument("-o", "--test_opt_arg", type=int, help="you can pass the 5 to see if it is woooorking!")

            subparser.set_defaults(func=cls.execute)

        @staticmethod
        def execute(repo, args) -> None:
            print(repo)

            if hasattr(args, 'test_pos_arg') and args.test_pos_arg == "y":
                print("args_worken!")
            else:
                print("nuh uh")
                print(args)

            if hasattr(args, 'test_opt_arg') and args.test_opt_arg == 5:
                print("opt arg is woooorking!")
    
    return ExampleCommand
