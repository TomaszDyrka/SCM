class Tree:
    """Represents a tree object storing directory entries and their metadata."""

    def __init__(self) -> None:
        """Initializes an empty Tree instance."""
        self.entries = []

    def add_entry(self,
                  entry_hash: str,
                  entry_type: str,
                  entry_name: str) -> None:
        """Adds an entry to the tree structure.

        Args:
            entry_hash: SHA-1 hash of the referenced object.
            entry_type: Type of the entry (e.g., 'blob' or 'tree').
            entry_name: Name of the file or directory.
        """
        self.entries.append({"hash": entry_hash,
                             "type": entry_type,
                             "name": entry_name})

    @property
    def header(self) -> str:
        """Constructs the header string containing object type and payload length.

        Returns:
            Formatted header string.
        """
        return f"tree {len(self.serialize_payload())}"

    def serialize_payload(self) -> bytes:
        """Serializes the tree entries into a formatted binary payload.

        Returns:
            Encoded binary representation of the tree entries.
        """
        rows = [f"{row['type']} {row['hash']} {row['name']}" for row in self.entries]
        return "\n".join(rows).encode()

    def serialize(self) -> bytes:
        """Serializes the tree object by prepending the header and null byte to the payload.

        Returns:
            Full binary payload of the serialized tree object.
        """
        return f"{self.header}\x00".encode() + self.serialize_payload()
