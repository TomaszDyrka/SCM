import pytest
from pathlib import Path
from src.repository.repository import Repository


@pytest.fixture
def temp_repo(tmp_path: Path):
    repo = Repository(tmp_path)

    yield repo
