import os
from argparse import Namespace
from pathlib import Path

from commands.commands.add_command import AddCommand
from commands.commands.init_command import InitCommand


class TestAddCommandFile:
    def test_add_single_file_from_root(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "sample.txt"
        test_file.write_bytes(b"hello world\n")

        args = Namespace(path=Path("sample.txt"))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        mode, blob_hash, relative_path = lines[0].strip().split()

        assert mode == "100644"
        assert relative_path == "sample.txt"

        object_dir = temp_repo.objects / blob_hash[:2]
        object_file = object_dir / blob_hash[2:]

        assert object_dir.is_dir()
        assert object_file.is_file()

    def test_add_single_file_from_subdirectory(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)
        sub_dir = repo_root / "src" / "nested"
        sub_dir.mkdir(parents=True, exist_ok=True)

        test_file = sub_dir / "code.py"
        test_file.write_bytes(b"print('hello')\n")

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        args = Namespace(path=Path(sub_dir / "code.py"))
        AddCommand.execute(temp_repo, args)
        print(temp_repo.repository_path)

        os.chdir(sub_dir)

        with open(temp_repo.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        mode, blob_hash, relative_path = lines[0].strip().split()

        assert mode == "100644"
        assert relative_path == "src/nested/code.py"

        object_dir = temp_repo.objects / blob_hash[:2]
        object_file = object_dir / blob_hash[2:]

        assert object_dir.is_dir()
        assert object_file.is_file()

    def test_add_file_preserves_object_content_and_hash(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_content = b"deterministic content"
        test_file = repo_root / "data.bin"
        test_file.write_bytes(test_content)

        args = Namespace(path=Path("data.bin"))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            line = f.readline()

        _, blob_hash, _ = line.strip().split()

        object_file = temp_repo.objects / blob_hash[:2] / blob_hash[2:]
        assert object_file.is_file()
        assert len(blob_hash) == 40

    def test_add_unmodified_file_does_not_duplicate_object(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"static content")

        args = Namespace(path=Path("file.txt"))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines_first_add = f.readlines()

        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines_second_add = f.readlines()

        assert len(lines_second_add) == 1
        assert lines_first_add == lines_second_add

    def test_add_modified_file_updates_index_and_creates_new_blob(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "file.txt"
        test_file.write_bytes(b"initial content")

        args = Namespace(path=Path("file.txt"))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            _, old_hash, _ = f.readline().strip().split()

        test_file.write_bytes(b"updated content")
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        _, new_hash, relative_path = lines[0].strip().split()

        assert relative_path == "file.txt"
        assert old_hash != new_hash

        old_blob = temp_repo.objects / old_hash[:2] / old_hash[2:]
        new_blob = temp_repo.objects / new_hash[:2] / new_hash[2:]

        assert old_blob.is_file()
        assert new_blob.is_file()

    def test_add_modified_file_from_nested_directory(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)
        nested_dir = repo_root / "src" / "app"
        nested_dir.mkdir(parents=True, exist_ok=True)

        test_file = nested_dir / "main.py"
        test_file.write_bytes(b"print('v1')")

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        args = Namespace(path=Path("src/app/main.py"))
        AddCommand.execute(temp_repo, args)

        test_file.write_bytes(b"print('v2')")
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        mode, new_hash, relative_path = lines[0].strip().split()

        assert mode == "100644"
        assert relative_path == "src/app/main.py"

        blob_file = temp_repo.objects / new_hash[:2] / new_hash[2:]
        assert blob_file.is_file()

    def test_add_directory_from_root(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        src_dir = repo_root / "src"
        nested_dir = src_dir / "nested"
        nested_dir.mkdir(parents=True, exist_ok=True)

        file1 = src_dir / "app.py"
        file2 = nested_dir / "utils.py"
        file1.write_bytes(b"print('app')")
        file2.write_bytes(b"print('utils')")

        args = Namespace(path=Path("src"))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines = [line.strip().split() for line in f]

        indexed_paths = {line[2] for line in lines}
        assert indexed_paths == {"src/app.py", "src/nested/utils.py"}

        for mode, blob_hash, _ in lines:
            assert mode in ("100644", "33206")
            blob_file = temp_repo.objects / blob_hash[:2] / blob_hash[2:]
            assert blob_file.is_file()

    def test_add_directory_from_subdirectory(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)
        modules_dir = repo_root / "modules"
        auth_dir = modules_dir / "auth"
        auth_dir.mkdir(parents=True, exist_ok=True)

        file1 = auth_dir / "login.py"
        file2 = auth_dir / "models.py"
        file1.write_bytes(b"def login(): pass")
        file2.write_bytes(b"class User: pass")

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        os.chdir(modules_dir)
        args = Namespace(path=Path("auth"))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines = [line.strip().split() for line in f]

        indexed_paths = {line[2] for line in lines}
        assert indexed_paths == {"modules/auth/login.py", "modules/auth/models.py"}

    def test_add_unmodified_directory_does_not_duplicate_objects(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        docs_dir = repo_root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        file1 = docs_dir / "readme.txt"
        file1.write_bytes(b"documentation content")

        args = Namespace(path=Path("docs"))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines_first_add = f.readlines()

        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines_second_add = f.readlines()

        assert len(lines_second_add) == 1
        assert lines_first_add == lines_second_add

    def test_add_modified_directory_updates_index_and_creates_new_blobs(
        self, temp_repo
    ):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        src_dir = repo_root / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

        file1 = src_dir / "main.py"
        file1.write_bytes(b"version 1")

        args = Namespace(path=Path("src"))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            _, old_hash, _ = f.readline().strip().split()

        file1.write_bytes(b"version 2")
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines = f.readlines()

        assert len(lines) == 1
        _, new_hash, relative_path = lines[0].strip().split()

        assert relative_path == "src/main.py"
        assert old_hash != new_hash

        old_blob = temp_repo.objects / old_hash[:2] / old_hash[2:]
        new_blob = temp_repo.objects / new_hash[:2] / new_hash[2:]

        assert old_blob.is_file()
        assert new_blob.is_file()

    def test_add_directory_ignores_rvn_folder(self, temp_repo):
        repo_root = temp_repo.repository_path.parent
        os.chdir(repo_root)

        InitCommand.execute(temp_repo, Namespace(path=Path("."), branch_name="master"))

        test_file = repo_root / "index.py"
        test_file.write_bytes(b"print('hello')")

        args = Namespace(path=Path("."))
        AddCommand.execute(temp_repo, args)

        with open(temp_repo.index, "r") as f:
            lines = [line.strip().split() for line in f]

        indexed_paths = [line[2] for line in lines]

        assert "index.py" in indexed_paths
        assert not any(".rvn" in path for path in indexed_paths)
