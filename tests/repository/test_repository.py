from src.repository.repository import compute_hash


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