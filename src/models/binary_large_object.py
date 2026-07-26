class BinaryLargeObject:
    """Represents a binary large object (blob) in the repository."""

    def __init__(self, content: bytes) -> None:
        """Initializes the BinaryLargeObject instance.

        Args:
            content: Raw binary content to be stored in the object.
        """
        self.content = content

    @property
    def header(self) -> str:
        """Constructs the header string containing object type and content length.

        Returns:
            Formatted header string.
        """
        return f"blob {len(self.content)}"

    def serialize(self) -> bytes:
        """Serializes the blob by prepending the header and null byte to the content.

        Returns:
            Serialized binary representation of the blob.
        """
        return f"{self.header}\x00".encode() + self.content
