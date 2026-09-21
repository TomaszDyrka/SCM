class Tree:
    """Represents a tree object storing directory entries and their metadata."""

    def __init__(self) -> None:
        """Initializes an empty Tree instance."""
        self.entries = []

    def add_entry(self, entry_hash: str, entry_type: str, entry_name: str) -> None:
        """Adds an entry to the tree structure.

        Args:
            entry_hash: SHA-1 hash of the referenced object.
            entry_type: Type of the entry (e.g., 'blob' or 'tree').
            entry_name: Name of the file or directory.
        """
        self.entries.append(
            {"hash": entry_hash, "type": entry_type, "name": entry_name}
        )

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
        sorted_entries = sorted(self.entries, key=lambda entry: entry["name"])

        rows = [
            f"{entry['type']} {entry['hash']} {entry['name']}"
            for entry in sorted_entries
        ]
        return "\n".join(rows).encode()

    def serialize(self) -> bytes:
        """Serializes the tree object by prepending the header and null byte to the payload.

        Returns:
            Full binary payload of the serialized tree object.
        """
        return f"{self.header}\x00".encode() + self.serialize_payload()

    @classmethod
    def deserialize(cls, data: bytes) -> "Tree":
        """Deserializes the tree object and creates new instance with the obtained data.

        Args:
            data: serialized tree in bytes.

        Returns:
            Deserialized tree.
        """

        _, payload = data.decode().split("\x00")
        clean_data = payload.split("\n")
        tree = cls()

        # line, after splitting by '\n', is made of 3 strings separated by spaces,
        # so we need to put them back into the function as arguments.
        # using a static structure of payload we can do it by simply getting exact
        # indices to correct keys
        # BUT here is the fun part:
        # add_entry recieves arguments in order: hash, type, name
        # and object serializes itself in order: type, hash, name
        # thus correct indices: 1 - 0 - 2

        clean_data.append("")
        while line := clean_data.pop(0):
            entry = line.split()
            tree.add_entry(entry[1], entry[0], " ".join(entry[2::]))

        return tree

    def __eq__(self, other: "Tree"):
        print(self.serialize())
        print(self.entries, "\n ---- \n ", other.entries)
        return self.entries == other.entries
