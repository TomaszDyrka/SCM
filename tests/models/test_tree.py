def test_tree_initialization_empty(create_tree):
    tree = create_tree()

    assert len(tree.entries) == 0
    assert tree.header == "tree 0"
    assert tree.serialize() == b"tree 0\x00"


def test_tree_add_entry(create_tree):
    tree = create_tree()
    tree.add_entry(
        entry_hash="4b825dc642cb6eb9a0f9e542d69221572b399201",
        entry_type="blob",
        entry_name="conftest.py",
    )

    assert len(tree.entries) == 1
    assert tree.entries[0]["name"] == "conftest.py"
    assert tree.entries[0]["type"] == "blob"
    assert (
        tree.entries[0]["hash"] == "4b825dc642cb6eb9a0f9e542d69221572b399201"
    )


def test_tree_serialize_payload_with_multiple_entries(create_tree):
    sample_entries = [
        {"hash": "1111111111111111111111111111111111111111", "type": "blob", "name": "main.py"},
        {"hash": "2222222222222222222222222222222222222222", "type": "tree", "name": "models"},
    ]
    tree = create_tree(entries=sample_entries)
    payload = tree.serialize_payload().decode()

    expected_rows = [
        "blob 1111111111111111111111111111111111111111 main.py",
        "tree 2222222222222222222222222222222222222222 models",
    ]
    assert payload == "\n".join(expected_rows)


def test_tree_full_serialization_binary_structure(create_tree):
    sample_entries = [
        {"hash": "abc12345", "type": "blob", "name": "test.py"}
    ]
    tree = create_tree(entries=sample_entries)
    serialized = tree.serialize()
    payload = tree.serialize_payload()
    header_bytes = f"{tree.header}\x00".encode()

    assert serialized.startswith(header_bytes)
    assert serialized == header_bytes + payload