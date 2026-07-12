import pytest
from src.models.binary_large_object import BinaryLargeObject


def test_blob_header_generation_with_content():
    content = b"hello world"
    blob = BinaryLargeObject(content)

    assert blob.header == "blob 11"


def test_blob_header_generation_empty_content():
    blob = BinaryLargeObject(b"")

    assert blob.header == "blob 0"


def test_blob_serialize_contains_null_byte_separator():
    content = b"test_data"
    blob = BinaryLargeObject(content)
    serialized = blob.serialize()

    expected_prefix = b"blob 9\x00"
    assert serialized.startswith(expected_prefix)
    assert serialized == expected_prefix + content


def test_blob_serialize_empty_content():
    blob = BinaryLargeObject(b"")
    serialized = blob.serialize()

    assert serialized == b"blob 0\x00"


def test_blob_content_remains_unchanged():
    content = b"binary\x01\x02\x03data"
    blob = BinaryLargeObject(content)

    assert blob.content == content