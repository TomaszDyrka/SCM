import pytest
from pathlib import Path
# from src.repository.repository import Repository
from src.models.binary_large_object import BinaryLargeObject

# @pytest.fixture
# def temp_repo(tmp_path: Path):
#     repo = Repository(tmp_path)
#
#     yield repo

@pytest.fixture
def temp_blob(content: bytes):
    blob = BinaryLargeObject(content)

    yield blob
