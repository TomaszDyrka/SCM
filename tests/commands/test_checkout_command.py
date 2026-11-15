import argparse
import os
from argparse import Namespace

import pytest

from commands.commands.checkout_command import CheckoutCommand
from models.commit import Commit
from models.tree import Tree


@pytest.mark.checkoutCommand
class TestCheckoutCommand:
    def test_register_parser(self):
        """tests if registration of parser is correct"""
        
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        CheckoutCommand.register_parser(subparsers)

        assert "checkout" in subparsers.choices
        checkout_parser = subparsers.choices["checkout"]
        
        actions = checkout_parser._actions
        target_action = next((a for a in actions if a.dest == "target"), None)

        assert target_action is not None
        assert checkout_parser._defaults["func"] == CheckoutCommand.execute

    def test_clean_home_dir_removes_only_tracked_files(self, temp_repo_initialized):
        """tests if tracked files are removed only"""
        
        repo_root = temp_repo_initialized.repository_path.parent
        os.chdir(repo_root)

        src_dir = repo_root / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        
        tracked_file = src_dir / "main.py"
        tracked_file.write_bytes(b"print('tracked')")
        
        untracked_file = repo_root / "config.ini"
        untracked_file.write_bytes(b"[settings]")

        with open(temp_repo_initialized.index, "w") as f:
            f.write("100644 dummyhash123 src/main.py\n")

        CheckoutCommand._clean_home_dir(temp_repo_initialized, repo_root)

        assert not tracked_file.exists()
        assert not src_dir.exists()
        assert untracked_file.exists()

    def test_restore_tree_writes_files_and_updates_index(self, temp_repo_initialized):
        """tests if restoring file and updating index works well"""
        
        repo_root = temp_repo_initialized.repository_path.parent
        os.chdir(repo_root)

        # Przygotowanie bloba i zapis z kompresją
        blob_content = b"blob 12\x00file content"
        blob_hash = temp_repo_initialized.write_object(blob_content)

        # Utworzenie obiektu Tree i zapis jego serializowanej formy
        tree = Tree()
        tree.add_entry(blob_hash, "blob", "restored.txt")
        tree_hash = temp_repo_initialized.write_object(tree.serialize())

        index_path = repo_root / "temp_index"
        with open(index_path, "w") as index_file:
            CheckoutCommand._restore_tree(temp_repo_initialized, tree_hash, repo_root, index_file)

        # Weryfikacja odtworzonego pliku
        restored = repo_root / "restored.txt"
        assert restored.is_file()
        assert restored.read_bytes() == b"file content"

        # Weryfikacja wpisu w nowym indeksie
        with open(index_path, "r") as index_file:
            lines = index_file.readlines()
        
        assert len(lines) == 1
        assert f"100644 {blob_hash} restored.txt\n" in lines

    def test_execute_detached_head_flow(self, temp_repo_initialized):
        """test case for detached head"""
        repo_root = temp_repo_initialized.repository_path.parent
        os.chdir(repo_root)

        empty_tree = Tree()
        tree_hash = temp_repo_initialized.write_object(empty_tree.serialize())

        commit = Commit(
            tree=tree_hash,
            parent_hashes=[],
            author="Test Author",
            timestamp="1234567890",
            committer="Test Committer",
            message="Test commit"
        )
        commit_hash = temp_repo_initialized.write_object(commit.serialize())

        args = Namespace(target=commit_hash)
        
        CheckoutCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.HEAD, "r") as head_file:
            head_content = head_file.read().strip()
            
        assert head_content == commit_hash
