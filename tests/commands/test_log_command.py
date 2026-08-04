import os
from argparse import Namespace
from pathlib import Path

from commands.commands.add_command import AddCommand
from commands.commands.commit_command import CommitCommand
from commands.commands.init_command import InitCommand
from commands.commands.log_command import LogCommand


class TestLogCommand:
    def test_log_single_commit(self, temp_repo, capsys):
        """Tests logging history when there is a single commit in the repository."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"content v1\n")

        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="First commit"))

        LogCommand.execute(temp_repo, Namespace(limit=-1))

        captured = capsys.readouterr()
        assert "First commit" in captured.out
        assert "Commit" in captured.out

    def test_log_multiple_commits_order(self, temp_repo, capsys):
        """Tests if commits are logged in reverse chronological order (newest first)."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"

        test_file.write_bytes(b"content v1\n")
        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="First commit"))

        test_file.write_bytes(b"content v2\n")
        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Second commit"))

        capsys.readouterr()
        LogCommand.execute(temp_repo, Namespace(limit=-1))

        captured = capsys.readouterr()
        assert captured.out.index("Second commit") < captured.out.index("First commit")

    def test_log_with_limit_flag(self, temp_repo, capsys):
        """Tests limiting the maximum number of logged commits using the limit option."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"

        test_file.write_bytes(b"v1\n")
        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Commit 1"))

        test_file.write_bytes(b"v2\n")
        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Commit 2"))

        capsys.readouterr()
        LogCommand.execute(temp_repo, Namespace(limit=1))

        captured = capsys.readouterr()
        assert "Commit 2" in captured.out
        assert "Commit 1" not in captured.out

    def test_log_detached_head_state(self, temp_repo, capsys):
        """Tests logging commit history when repository is in a detached HEAD state."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"detached content\n")

        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Detached commit"))

        branch_name = Path(temp_repo.read_head().split()[1]).name
        commit_hash = temp_repo.read_branch(branch_name)

        temp_repo.update_head_hash(commit_hash)

        LogCommand.execute(temp_repo, Namespace(limit=-1))

        captured = capsys.readouterr()
        assert "Detached commit" in captured.out
        assert commit_hash in captured.out

    def test_log_from_subdirectory(self, temp_repo, capsys):
        """Tests executing the log command from inside a nested subdirectory."""
        repo_root = temp_repo.repository_path.parent
        sub_dir = repo_root / "src" / "nested"
        sub_dir.mkdir(parents=True, exist_ok=True)

        os.chdir(repo_root)
        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"content\n")

        AddCommand.execute(temp_repo, Namespace(path=Path("file.txt")))
        CommitCommand.execute(temp_repo, Namespace(message="Root commit"))

        os.chdir(sub_dir)
        LogCommand.execute(temp_repo, Namespace(limit=-1))

        captured = capsys.readouterr()
        assert "Root commit" in captured.out

    def test_log_uninitialized_repository(self, temp_repo, capsys):
        """Tests log command behavior when invoked inside an uninitialized repository."""
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        LogCommand.execute(temp_repo, Namespace(limit=-1))

        captured = capsys.readouterr()
        assert "Repository has not been initialized yet" in captured.out or "Nothing to log" in captured.out
