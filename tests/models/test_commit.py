def test_commit_header_generation(temp_commit):
    payload_length = len(temp_commit.serialize_payload())

    assert temp_commit.header == f"commit {payload_length}"


def test_commit_serialization_format(temp_commit):
    payload = temp_commit.serialize_payload().decode()

    expected_lines = [
        "tree default_tree_hash",
        "parent default_parent_hash",
        "author John Doe 1700000000",
        "committer John Doe 1700000000",
        "",
        "Default commit message",
    ]
    assert payload == "\n".join(expected_lines)


def test_commit_full_serialization_binary_structure(temp_commit):
    serialized = temp_commit.serialize()
    payload = temp_commit.serialize_payload()
    header_bytes = f"{temp_commit.header}\x00".encode()

    assert serialized.startswith(header_bytes)
    assert serialized == header_bytes + payload


def test_commit_timestamp_type_handling(temp_commit):
    assert temp_commit.timestamp == "1700000000"