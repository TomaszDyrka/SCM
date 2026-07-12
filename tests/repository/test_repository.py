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