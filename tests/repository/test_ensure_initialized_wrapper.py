import pytest


@pytest.mark.parametrize(
    "method_call",
    [
        lambda repo: repo.write_object(b"content"),
        lambda repo: repo.update_branch("master", "hash"),
        lambda repo: repo.update_head_path("master"),
        lambda repo: repo.update_head_hash("hash"),
        lambda repo: repo.read_object("0000000000000000000000000000000000000000"),
        lambda repo: repo.read_branch("master"),
    ],
)

# TODO
# maybe a little shorter name? xd
# ur call m8
def test_all_repository_methods_raise_runtime_error_when_not_initialized(
    temp_repo, method_call
):
    with pytest.raises(RuntimeError) as exc_info:
        method_call(temp_repo)

    assert "Repository is not initialized" in str(exc_info.value)
