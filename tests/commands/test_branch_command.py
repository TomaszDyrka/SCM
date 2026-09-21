import argparse
import os
from argparse import Namespace

from unittest.mock import patch
import pytest

from commands.commands.branch_command import BranchCommand
from commands.commands.commit_command import CommitCommand
from models.commit import Commit
from models.tree import Tree


@pytest.mark.branchCommand
class TestBranchCommand:
    def test_register_parser(self):
        """Tests if registration of parser is correct."""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        BranchCommand.register_parser(subparsers)

        assert "branch" in subparsers.choices
        branch_parser = subparsers.choices["branch"]
        
        actions = branch_parser._actions
        target_action = next((a for a in actions if a.dest == "name"), None)

        assert target_action is not None
        assert branch_parser._defaults["func"] == BranchCommand.execute

    def test_creating_branch_from_ref(self, temp_repo_initialized):
        """Tests creating a branch when HEAD points to another branch (ref)."""
        repo = temp_repo_initialized
        args = Namespace(name="new_feature")
        
        main_branch_path = repo.refs / "heads" / "main"
        main_branch_path.parent.mkdir(parents=True, exist_ok=True)
        main_branch_path.write_text("dummy_hash_12345")
        repo.HEAD.write_text("ref: refs/heads/main\n")

        BranchCommand.execute(repo, args)

        new_branch_path = repo.refs / "heads" / "new_feature"
        assert new_branch_path.is_file(), "Plik nowej gałęzi nie został utworzony."
        assert new_branch_path.read_text() == "dummy_hash_12345", "Nowa gałąź ma nieprawidłowy hash."

    def test_creating_branch_from_detached_head(self, temp_repo_initialized):
        """Tests creating a branch when HEAD is directly a commit hash."""
        repo = temp_repo_initialized
        args = Namespace(name="rescue_branch")
        
        repo.HEAD.write_text("detached_hash_98765\n")

        BranchCommand.execute(repo, args)

        new_branch_path = repo.refs / "heads" / "rescue_branch"
        assert new_branch_path.is_file(), "Plik gałęzi z detached HEAD nie został utworzony."
        assert new_branch_path.read_text() == "detached_hash_98765"

    def test_branch_already_exists_error(self, temp_repo_initialized, capsys):
        """Tests if creating an already existing branch raises error and doesn't overwrite it."""
        repo = temp_repo_initialized
        args = Namespace(name="existing_branch")
        
        branch_path = repo.refs / "heads" / "existing_branch"
        branch_path.parent.mkdir(parents=True, exist_ok=True)
        branch_path.write_text("old_hash")
        
        repo.HEAD.write_text("new_hash\n")

        BranchCommand.execute(repo, args)

        assert branch_path.read_text() == "old_hash", "Istniejąca gałąź została niepotrzebnie nadpisana!"
        
        captured = capsys.readouterr()
        assert "already exists" in captured.out or "already exists" in captured.err

    def test_repo_not_initialized_error(self, temp_repo_initialized, capsys):
        """Tests handling FileNotFoundError when HEAD is missing."""
        repo = temp_repo_initialized
        args = Namespace(name="test_branch")
        
        repo.HEAD.unlink(missing_ok=True)

        BranchCommand.execute(repo, args)

        captured = capsys.readouterr()
        expected_msg = "Repository has not been initialized yet"
        assert expected_msg in captured.out or expected_msg in captured.err
