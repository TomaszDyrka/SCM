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

    def test_add_unmodified_file_does_not_duplicate_object(self, temp_repo_initialized):
        repo_root = temp_repo_initialized.repository_path.parent
        os.chdir(repo_root)

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"static content")

        args = Namespace(path=Path("file.txt"))
        AddCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.index, "r") as f:
            lines_first_add = f.readlines()

        AddCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.index, "r") as f:
            lines_second_add = f.readlines()

        assert len(lines_second_add) == 1
        assert lines_first_add == lines_second_add

    def test_add_modified_file_updates_index_and_creates_new_blob(self, temp_repo_initialized):
        repo_root = temp_repo_initialized.repository_path.parent
        os.chdir(repo_root)

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"initial content")

        args = Namespace(path=Path("file.txt"))
        AddCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.index, "r") as f:
            _, old_hash, _ = f.readline().strip().split()

        test_file.write_bytes(b"updated content")
        AddCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        _, new_hash, relative_path = lines[0].strip().split()

        assert relative_path == "file.txt"
        assert old_hash != new_hash

        old_blob = temp_repo_initialized.objects / old_hash[:2] / old_hash[2:]
        new_blob = temp_repo_initialized.objects / new_hash[:2] / new_hash[2:]

        assert old_blob.is_file()
        assert new_blob.is_file()

    def test_add_modified_file_from_nested_directory(self, temp_repo_initialized):
        repo_root = temp_repo_initialized.repository_path.parent
        nested_dir = repo_root / "src" / "app"
        nested_dir.mkdir(parents=True, exist_ok=True)

        test_file = nested_dir / "main.py"
        test_file.write_bytes(b"print('v1')")

        os.chdir(nested_dir)

        args = Namespace(path=Path("main.py"))
        AddCommand.execute(temp_repo_initialized, args)

        test_file.write_bytes(b"print('v2')")
        AddCommand.execute(temp_repo_initialized, args)

        with open(temp_repo_initialized.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        mode, new_hash, relative_path = lines[0].strip().split()

        assert mode == "100644"
        assert relative_path == "src/app/main.py"

        blob_file = temp_repo_initialized.objects / new_hash[:2] / new_hash[2:]
        assert blob_file.is_file()
