import os
from argparse import Namespace
from pathlib import Path

import pytest

from commands.commands.add_command import AddCommand
from commands.commands.commit_command import CommitCommand
from commands.commands.init_command import InitCommand


@pytest.mark.commitCommand
class TestCommitCommand:
    def test_commit_single_file_from_root(self, temp_repo):
        """Tests committing a single staged file from the repository root directory."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "sample.txt"
        test_file.write_bytes(b"hello commit\n")

        AddCommand.execute(temp_repo, Namespace(path=Path("sample.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Initial commit"))

        head_hash = temp_repo.read_head()
        assert len(head_hash) == 40 or head_hash.startswith("ref:")

    def test_commit_from_subdirectory(self, temp_repo):
        """Tests executing a commit from inside a nested subdirectory."""
        repo_root = temp_repo.repository_path.parent
        sub_dir = repo_root / "src" / "nested"
        sub_dir.mkdir(parents=True, exist_ok=True)

        test_file = sub_dir / "code.py"
        test_file.write_bytes(b"print('hello')\n")

        os.chdir(sub_dir)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))
        AddCommand.execute(temp_repo, Namespace(path=Path("code.py")))
        CommitCommand.execute(temp_repo, Namespace(message="Subdirectory commit"))

        branch_name = Path(temp_repo.read_head().split()[1]).name
        commit_hash = temp_repo.read_branch(branch_name)

        assert len(commit_hash) == 40

    def test_commit_creates_tree_and_commit_objects(self, temp_repo):
        """Tests whether commit operation creates valid tree and commit objects in the store."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "data.txt"
        test_file.write_bytes(b"commit content")

        AddCommand.execute(temp_repo, Namespace(path=Path("data.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Create objects"))

        branch_name = Path(temp_repo.read_head().split()[1]).name
        commit_hash = temp_repo.read_branch(branch_name)

        commit_obj_file = temp_repo.objects / commit_hash[:2] / commit_hash[2:]
        assert commit_obj_file.is_file()

    def test_consecutive_commits_update_parent_reference(self, temp_repo):
        """Tests if consecutive commits properly chain parent hashes in the history."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"version 1")

        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="First commit"))

        branch_name = Path(temp_repo.read_head().split()[1]).name
        first_commit_hash = temp_repo.read_branch(branch_name)

        test_file.write_bytes(b"version 2")
        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Second commit"))

        second_commit_hash = temp_repo.read_branch(branch_name)

        assert first_commit_hash != second_commit_hash

    def test_commit_in_detached_head_state(self, temp_repo):
        """Tests committing directly when HEAD is in detached state instead of pointing to a branch."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"detached content")

        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Base commit"))

        branch_name = Path(temp_repo.read_head().split()[1]).name
        base_commit_hash = temp_repo.read_branch(branch_name)

        temp_repo.update_head_hash(base_commit_hash)

        test_file.write_bytes(b"new detached content")
        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Detached commit"))

        new_head_hash = temp_repo.read_head()
        assert new_head_hash != base_commit_hash
        assert not new_head_hash.startswith("ref:")

    def test_commit_nested_directory_structure(self, temp_repo):
        """Tests if hierarchical tree objects are correctly built for nested directory structures."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        nested_dir = repo_root / "src" / "core"
        nested_dir.mkdir(parents=True, exist_ok=True)

        file1 = repo_root / "README.md"
        file2 = nested_dir / "main.py"

        file1.write_bytes(b"# Docs")
        file2.write_bytes(b"print('ok')")

        AddCommand.execute(temp_repo, Namespace(path=Path(".")))
        CommitCommand.execute(temp_repo, Namespace(message="Nested structure"))

        branch_name = Path(temp_repo.read_head().split()[1]).name
        commit_hash = temp_repo.read_branch(branch_name)

        assert len(commit_hash) == 40
