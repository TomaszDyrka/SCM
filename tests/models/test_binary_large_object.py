import pytest


@pytest.mark.modelBlob
class TestModelBlob:
    """Test blob properties"""

    def test_blob_header_generation_with_content(self, create_blob):
        """tests blob header if proper conent provided"""

        blob = create_blob(content=b"hello world")
        assert blob.header == "blob 11"

    def test_blob_header_generation_empty_content(self, create_blob):
        """tests blob header if empty content provided"""

        blob = create_blob(content=b"")
        assert blob.header == "blob 0"

    def test_blob_serialize_contains_null_byte_separator(self, create_blob):
        """tests if data has been sucessfully encoded"""

        content = b"test_data"
        blob = create_blob(content=content)
        serialized = blob.serialize()

        expected_prefix = b"blob 9\x00"
        
        assert serialized.startswith(expected_prefix)
        assert serialized == expected_prefix + content

    def test_blob_serialize_empty_content(self, create_blob):
        """tests if data has been sucessfully encoded despite no empty content"""

        blob = create_blob(content=b"")
        serialized = blob.serialize()

        assert serialized == b"blob 0\x00"

    def test_blob_content_remains_unchanged(self, create_blob):
        """tests if encoded content is consistent"""

        content = b"binary\x01\x02\x03data"
        blob = create_blob(content=content)

        assert blob.content == content
