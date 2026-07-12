def test_initialize_directories_creates_correct_structure(temp_repo):
    temp_repo.initialize_directories()

    assert temp_repo.objects.exists()
    assert temp_repo.refs.exists()
    assert temp_repo.HEAD.exists()

    assert (temp_repo.repository_path / "objects").exists()
    assert (temp_repo.repository_path / "refs").exists()
    assert (temp_repo.repository_path / "HEAD.txt").exists()

def test_initialize_directories_creates_correct_types(temp_repo):
    temp_repo.initialize_directories()

    assert temp_repo.objects.is_dir()
    assert temp_repo.refs.is_dir()

    assert temp_repo.HEAD.is_file()