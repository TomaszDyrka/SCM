from pathlib import Path

import pytest

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
