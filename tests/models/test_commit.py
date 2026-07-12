def test_commit_timestamp_type_handling(create_commit):
    commit = create_commit(timestamp="1700000000")

    assert commit.timestamp == "1700000000"


def test_commit_header_generation(create_commit):
    commit = create_commit()
    payload_length = len(commit.serialize_payload())

    assert commit.header == f"commit {payload_length}"


def test_commit_serialization_format(create_commit):
    commit = create_commit(
        tree="custom_tree",
        parent_hashes=["custom_parent"],
        author="Alice",
        committer="Bob",
        message="Feature implementation",
        timestamp="1800000000",
    )
    payload = commit.serialize_payload().decode()

    expected_lines = [
        "tree custom_tree",
        "parent custom_parent",
        "author Alice 1800000000",
        "committer Bob 1800000000",
        "",
        "Feature implementation",
    ]
    assert payload == "\n".join(expected_lines)


def test_commit_serialize_payload_multiple_parents_merge(create_commit):
    commit = create_commit(parent_hashes=["parent_1", "parent_2"])
    payload = commit.serialize_payload().decode()

    assert "parent parent_1\nparent parent_2" in payload


def test_commit_serialize_payload_no_parents_root_commit(create_commit):
    commit = create_commit(parent_hashes=[])
    payload = commit.serialize_payload().decode()

    assert "parent" not in payload


def test_commit_full_serialization_binary_structure(create_commit):
    commit = create_commit()
    serialized = commit.serialize()
    payload = commit.serialize_payload()
    header_bytes = f"{commit.header}\x00".encode()

    assert serialized.startswith(header_bytes)
    assert serialized == header_bytes + payload