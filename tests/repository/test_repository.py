import pytest
from src.repository.repository import compute_hash
import zlib


def test_initialize_directories_creates_correct_structure(temp_repo):
    temp_repo.initialize_directories()

    # Check if all paths exist
    assert temp_repo.objects.exists()
    assert temp_repo.refs.exists()
    assert temp_repo.HEAD.exists()

    # Check if all elements are in the main .smc file
    assert (temp_repo.repository_path / "objects").exists()
    assert (temp_repo.repository_path / "refs").exists()
    assert (temp_repo.repository_path / "HEAD.txt").exists()

def test_initialize_directories_creates_correct_types(temp_repo):
    temp_repo.initialize_directories()

    # Check if `objects` and `refs` ar folders
    assert temp_repo.objects.is_dir()
    assert temp_repo.refs.is_dir()

    # Check if `HEAD.txt` is a file
    assert temp_repo.HEAD.is_file()

def test_hashing_algorithm():
    # Check if hash has the expected value
    first_hash = compute_hash(b"scm")

    assert first_hash == "c254eda801bce04e1df6ae386a0fe0292fd3aca5"

    # Check if hash is deterministic
    second_hash = compute_hash(b"scm")

    assert first_hash == second_hash

def test_write_object_saves_compressed_file_in_correct_folder(temp_repo):
    temp_repo.initialize_directories()

    test_content = b"scm test content"

    returned_hash = temp_repo.write_object(test_content)

    expected_folder = temp_repo.objects / returned_hash[:2]
    expected_file = expected_folder / returned_hash[2:]

    assert expected_folder.is_dir()
    assert expected_file.is_file()

def test_write_objects_compressed_content_matches_input_after_decompression(temp_repo):
    temp_repo.initialize_directories()

    test_content = b"scm test content"

    returned_hash = temp_repo.write_object(test_content)

    expected_folder = temp_repo.objects / returned_hash[:2]
    expected_file = expected_folder / returned_hash[2:]

    with open(expected_file, "rb") as f:
        saved_bytes = f.read()

    assert zlib.decompress(saved_bytes) == test_content

def test_update_branch_structure_and_file_content_are_correct(temp_repo):
    temp_repo.initialize_directories()

    name = "master"

    metadata = """
    commit 228\x00tree 4a5e12b9c30b2c1a4d5e6f7a8b9c0d1e2f3a4b5c
    parent 1c2b3a4f5e6d7c8b9a0f1e2d3c4b5a6f7e8d9c0b
    author Jan Kowalski jan@kowalski.pl 1717593600 +0200
    committer Jan Kowalski jan@kowalski.pl 1717593600 +0200
    
    First commit message
    """

    temp_repo.update_branch(name, metadata)
    branch_file = (temp_repo.refs / "heads" / name)

    assert branch_file.is_file()

    with open(branch_file, "r") as f:
        saved_hash = f.read()

    assert saved_hash == compute_hash(metadata.encode())

def test_update_head_path_file_content_is_correct(temp_repo):
    temp_repo.initialize_directories()

    branch_name = "test_branch"
    temp_repo.update_head_path(branch_name)

    with open(temp_repo.HEAD, "r") as f:
        saved_path = f.read()

    assert saved_path == f"ref: refs/heads/{branch_name}"


def test_update_head_hash_file_content_is_correct(temp_repo):
    temp_repo.initialize_directories()

    commit_hash = "d0ba1fb9ef60b7487f40c42c22b6091327fa24e2"
    temp_repo.update_head_hash(commit_hash)

    with open(temp_repo.HEAD, "r") as f:
        saved_path = f.read()

    assert saved_path == commit_hash

def test_read_object_is_saved_and_loaded_content_the_same(temp_repo):
    temp_repo.initialize_directories()

    test_content = b"scm test content"

    object_hash = temp_repo.write_object(test_content)
    saved_content = temp_repo.read_object(object_hash)

    assert test_content == saved_content

def test_read_object_raises_file_not_found_for_missing_hash(temp_repo):
    temp_repo.initialize_directories()

    fake_hash = "0000000000000000000000000000000000000000"

    with pytest.raises(FileNotFoundError) as exc_info:
        temp_repo.read_object(fake_hash)

    assert f"Object {fake_hash} does not exist in the repository." in str(exc_info.value)


import pytest


def test_read_branch_success_and_failure(temp_repo):
    temp_repo.initialize_directories()

    branch_name = "feature-login"
    commit_metadata = """
        commit 228\x00tree 4a5e12b9c30b2c1a4d5e6f7a8b9c0d1e2f3a4b5c
        parent 1c2b3a4f5e6d7c8b9a0f1e2d3c4b5a6f7e8d9c0b
        author Jan Kowalski jan@kowalski.pl 1717593600 +0200
        committer Jan Kowalski jan@kowalski.pl 1717593600 +0200
        
        First commit message
    """

    temp_repo.update_branch(branch_name, commit_metadata)
    saved_hash = temp_repo.read_branch(branch_name)
    metadata_hash = compute_hash(commit_metadata.encode())

    assert metadata_hash == saved_hash

    missing_branch = "non-existent-branch"
    with pytest.raises(FileNotFoundError) as exc_info:
        temp_repo.read_branch(missing_branch)

    assert f"Branch {missing_branch} does not exist in the repository." in str(exc_info.value)