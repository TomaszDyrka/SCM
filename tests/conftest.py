import pytest
from pathlib import Path
# from src.repository.repository import Repository
from src.models.binary_large_object import BinaryLargeObject
from src.models.commit import Commit

# @pytest.fixture
# def temp_repo(tmp_path: Path):
#     repo = Repository(tmp_path)
#
#     yield repo

@pytest.fixture
def temp_commit() -> Commit:
    return Commit(
        tree="default_tree_hash",
        parent_hashes=["default_parent_hash"],
        author="John Doe",
        committer="John Doe",
        message="Default commit message",
        timestamp="1700000000",
    )