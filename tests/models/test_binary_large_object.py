def test_blob_header_generation_with_content(create_blob):
    blob = create_blob(content=b"hello world")

    assert blob.header == "blob 11"


def test_blob_header_generation_empty_content(create_blob):
    blob = create_blob(content=b"")

    assert blob.header == "blob 0"


def test_blob_serialize_contains_null_byte_separator(create_blob):
    content = b"test_data"
    blob = create_blob(content=content)
    serialized = blob.serialize()

    expected_prefix = b"blob 9\x00"
    assert serialized.startswith(expected_prefix)
    assert serialized == expected_prefix + content


def test_blob_serialize_empty_content(create_blob):
    blob = create_blob(content=b"")
    serialized = blob.serialize()

    assert serialized == b"blob 0\x00"


def test_blob_content_remains_unchanged(create_blob):
    content = b"binary\x01\x02\x03data"
    blob = create_blob(content=content)

    assert blob.content == content