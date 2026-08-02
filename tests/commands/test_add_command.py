import os
from argparse import Namespace
from pathlib import Path
from commands.commands.add_command import AddCommand


class TestAddCommandFile:
    def test_add_single_file_from_root(self, temp_repo_initialized):
        repo_root = temp_repo_initialized.repository_path.parent
        os.chdir(repo_root)

        test_file = repo_root / "sample.txt"
        test_file.write_bytes(b"hello world\n")

        args = Namespace(path=Path("sample.txt"))
        AddCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        mode, blob_hash, relative_path = lines[0].strip().split()

        assert mode == "100644"
        assert relative_path == "sample.txt"

        object_dir = temp_repo_initialized.objects / blob_hash[:2]
        object_file = object_dir / blob_hash[2:]

        assert object_dir.is_dir()
        assert object_file.is_file()

    def test_add_single_file_from_subdirectory(self, temp_repo_initialized):
        repo_root = temp_repo_initialized.repository_path.parent
        sub_dir = repo_root / "src" / "nested"
        sub_dir.mkdir(parents=True, exist_ok=True)

        test_file = sub_dir / "code.py"
        test_file.write_bytes(b"print('hello')\n")

        os.chdir(sub_dir)

        args = Namespace(path=Path("code.py"))
        AddCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        mode, blob_hash, relative_path = lines[0].strip().split()

        assert mode == "100644"
        assert relative_path == "src/nested/code.py"

        object_dir = temp_repo_initialized.objects / blob_hash[:2]
        object_file = object_dir / blob_hash[2:]

        assert object_dir.is_dir()
        assert object_file.is_file()

    def test_add_file_preserves_object_content_and_hash(self, temp_repo_initialized):
        repo_root = temp_repo_initialized.repository_path.parent
        os.chdir(repo_root)

        test_content = b"deterministic content"
        test_file = repo_root / "data.bin"
        test_file.write_bytes(test_content)

        args = Namespace(path=Path("data.bin"))
        AddCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.index, "r") as f:
            line = f.readline()

        _, blob_hash, _ = line.strip().split()

        object_file = temp_repo_initialized.objects / blob_hash[:2] / blob_hash[2:]
        assert object_file.is_file()
        assert len(blob_hash) == 40