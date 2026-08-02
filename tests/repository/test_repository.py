import os
import zlib

import pytest

from src.models.binary_large_object import BinaryLargeObject
from src.repository.repository import compute_hash


@pytest.mark.repository
class TestRepository:
    """Tests repository features"""

    def test_initialize_directories_creates_correct_structure(self, temp_repo):
        """tests if initialization creates correct structure"""

        temp_repo.initialize_directories()

        # Check if all paths exist
        assert temp_repo.objects.exists()
        assert temp_repo.refs.exists()
        assert temp_repo.HEAD.exists()

        # Check if all elements are in the main .smc file
        assert (temp_repo.repository_path / "objects").exists()
        assert (temp_repo.repository_path / "refs").exists()
        assert (temp_repo.repository_path / "HEAD.txt").exists()

    def test_initialize_directories_creates_correct_types(self, temp_repo):
        """tests if initialization creates correct types (dirs)"""

        temp_repo.initialize_directories()

        # Check if `objects` and `refs` ar folders
        assert temp_repo.objects.is_dir()
        assert temp_repo.refs.is_dir()

        # Check if `HEAD.txt` is a file
        assert temp_repo.HEAD.is_file()

    def test_hashing_algorithm(self):
        """tests if hashing algo producing correct outcome"""

        # Check if hash has the expected value
        first_hash = compute_hash(b"scm")

        assert first_hash == "c254eda801bce04e1df6ae386a0fe0292fd3aca5"

        # Check if hash is deterministic
        second_hash = compute_hash(b"scm")

        assert first_hash == second_hash

    def test_write_object_saves_compressed_file_in_correct_folder(
        self, temp_repo_initialized
    ):
        os.chdir(temp_repo_initialized.repository_path.parent)
        test_content = b"scm test content"

        returned_hash = temp_repo_initialized.write_object(test_content)

        expected_folder = temp_repo_initialized.objects / returned_hash[:2]
        expected_file = expected_folder / returned_hash[2:]

        assert expected_folder.is_dir()
        assert expected_file.is_file()

    def test_write_objects_compressed_content_matches_input_after_decompression(
        self, temp_repo_initialized
    ):
        os.chdir(temp_repo_initialized.repository_path.parent)
        test_content = b"scm test content"

        returned_hash = temp_repo_initialized.write_object(test_content)

        expected_folder = temp_repo_initialized.objects / returned_hash[:2]
        expected_file = expected_folder / returned_hash[2:]

        with open(expected_file, "rb") as f:
            saved_bytes = f.read()

        assert zlib.decompress(saved_bytes) == test_content

    def test_update_branch_structure_and_file_content_are_correct(
        self, temp_repo_initialized
    ):
        os.chdir(temp_repo_initialized.repository_path.parent)
        name = "master"

        metadata = """
        commit 228\x00tree 4a5e12b9c30b2c1a4d5e6f7a8b9c0d1e2f3a4b5c
        parent 1c2b3a4f5e6d7c8b9a0f1e2d3c4b5a6f7e8d9c0b
        author Jan Kowalski jan@kowalski.pl 1717593600 +0200
        committer Jan Kowalski jan@kowalski.pl 1717593600 +0200
        
        First commit message
        """

        temp_repo_initialized.update_branch(name, metadata)
        branch_file = temp_repo_initialized.refs / "heads" / name

        assert branch_file.is_file()

        with open(branch_file, "r") as f:
            saved_hash = f.read()

        assert saved_hash == compute_hash(metadata.encode())

    def test_update_head_path_file_content_is_correct(self, temp_repo_initialized):
        os.chdir(temp_repo_initialized.repository_path.parent)
        branch_name = "test_branch"
        temp_repo_initialized.update_head_path(branch_name)

        with open(temp_repo_initialized.HEAD, "r") as f:
            saved_path = f.read()

        assert saved_path == f"ref: refs/heads/{branch_name}"

    def test_update_head_hash_file_content_is_correct(self, temp_repo_initialized):
        os.chdir(temp_repo_initialized.repository_path.parent)
        commit_hash = "d0ba1fb9ef60b7487f40c42c22b6091327fa24e2"
        temp_repo_initialized.update_head_hash(commit_hash)

        with open(temp_repo_initialized.HEAD, "r") as f:
            saved_path = f.read()

        assert saved_path == commit_hash

    def test_read_object_is_saved_and_loaded_content_the_same(
        self, temp_repo_initialized
    ):
        os.chdir(temp_repo_initialized.repository_path.parent)
        test_content = b"scm test content"

        object_hash = temp_repo_initialized.write_object(test_content)
        saved_content = temp_repo_initialized.read_object(object_hash)

        assert test_content == saved_content

    def test_read_object_raises_file_not_found_for_missing_hash(
        self, temp_repo_initialized
    ):
        os.chdir(temp_repo_initialized.repository_path.parent)
        fake_hash = "0000000000000000000000000000000000000000"

        with pytest.raises(FileNotFoundError) as exc_info:
            temp_repo_initialized.read_object(fake_hash)

        assert f"Object {fake_hash} does not exist in the repository." in str(
            exc_info.value
        )

    def test_read_branch_success_and_failure(self, temp_repo_initialized):
        os.chdir(temp_repo_initialized.repository_path.parent)
        branch_name = "feature-login"
        commit_metadata = """
            commit 228\x00tree 4a5e12b9c30b2c1a4d5e6f7a8b9c0d1e2f3a4b5c
            parent 1c2b3a4f5e6d7c8b9a0f1e2d3c4b5a6f7e8d9c0b
            author Jan Kowalski jan@kowalski.pl 1717593600 +0200
            committer Jan Kowalski jan@kowalski.pl 1717593600 +0200
            
            First commit message
        """

        temp_repo_initialized.update_branch(branch_name, commit_metadata)
        saved_hash = temp_repo_initialized.read_branch(branch_name)
        metadata_hash = compute_hash(commit_metadata.encode())

        assert metadata_hash == saved_hash

        missing_branch = "non-existent-branch"
        with pytest.raises(FileNotFoundError) as exc_info:
            temp_repo_initialized.read_branch(missing_branch)

        assert f"Branch {missing_branch} does not exist in the repository." in str(
            exc_info.value
        )

    def test_read_head_input_and_saved_values_match(self, temp_repo_initialized):
        os.chdir(temp_repo_initialized.repository_path.parent)
        name = "master"
        temp_repo_initialized.update_head_path(name)
        updated_head = temp_repo_initialized.read_head()

        assert updated_head == f"ref: refs/heads/{name}"

        commit_hash = "d0ba1fb9ef60b7487f40c42c22b6091327fa24e2"
        temp_repo_initialized.update_head_hash(commit_hash)
        updated_head = temp_repo_initialized.read_head()

        assert updated_head == commit_hash

    def test_add_file_to_index_creates_entry_in_index_file(self, temp_repo_initialized):
        os.chdir(temp_repo_initialized.repository_path.parent)
        test_file = temp_repo_initialized.repository_path.parent / "main.py"
        test_file.write_text("print('hello')")

        blob = BinaryLargeObject(b"print('hello')")
        blob_hash = temp_repo_initialized.write_object(blob.serialize())

        temp_repo_initialized.add_file_to_index(test_file, blob)

        assert temp_repo_initialized.index.is_file()

        entries = temp_repo_initialized.read_index()
        assert "main.py" in entries
        print(entries)
        assert entries["main.py"].hash == blob_hash

    def test_add_file_to_index_updates_existing_entry(self, temp_repo_initialized):
        os.chdir(temp_repo_initialized.repository_path.parent)
        test_file = temp_repo_initialized.repository_path.parent / "main.py"
        test_file.write_text("v1")

        blob_v1 = BinaryLargeObject(b"v1")
        temp_repo_initialized.write_object(blob_v1.serialize())
        temp_repo_initialized.add_file_to_index(test_file, blob_v1)

        test_file.write_text("v2")
        blob_v2 = BinaryLargeObject(b"v2")
        blob_v2_hash = temp_repo_initialized.write_object(blob_v2.serialize())
        temp_repo_initialized.add_file_to_index(test_file, blob_v2)

        entries = temp_repo_initialized.read_index()
        assert len(entries) == 1
        assert entries["main.py"].hash == blob_v2_hash

    def test_read_index_returns_empty_dict_when_index_file_missing(
        self, temp_repo_initialized
    ):
        os.chdir(temp_repo_initialized.repository_path.parent)
        entries = temp_repo_initialized.read_index()

        assert entries == {}

    def test_read_index_parses_multiple_files_correctly(self, temp_repo_initialized):
        os.chdir(temp_repo_initialized.repository_path.parent)
        file_a = temp_repo_initialized.repository_path.parent / "a.txt"
        file_b = temp_repo_initialized.repository_path.parent / "src" / "b.txt"
        file_b.parent.mkdir(parents=True, exist_ok=True)

        file_a.write_text("content_a")
        file_b.write_text("content_b")

        blob_a = BinaryLargeObject(b"content_a")
        blob_b = BinaryLargeObject(b"content_b")

        temp_repo_initialized.write_object(blob_a.serialize())
        temp_repo_initialized.write_object(blob_b.serialize())

        temp_repo_initialized.add_file_to_index(file_a, blob_a)
        temp_repo_initialized.add_file_to_index(file_b, blob_b)

        entries = temp_repo_initialized.read_index()

        assert len(entries) == 2
        assert "a.txt" in entries
        assert "src/b.txt" in entries or "src\\b.txt" in entries
