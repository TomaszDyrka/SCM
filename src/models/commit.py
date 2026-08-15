class Commit:
    """Represents a commit object containing tree structure, parent hashes, and metadata."""

    def __init__(
        self,
        tree: str,
        parent_hashes: list[str],
        author: str,
        timestamp: str,
        committer: str,
        message: str,
    ) -> None:
        """Initializes the Commit instance.

        Args:
            tree: SHA-1 hash of the root tree object for this commit.
            parent_hashes: List of SHA-1 hashes of parent commits.
            author: Author information string.
            timestamp: Timestamp string indicating when the commit was created.
            committer: Committer information string.
            message: Commit message detailing the changes.
        """
        self.tree = tree
        self.parent_hashes = parent_hashes
        self.author = author
        self.timestamp = timestamp
        self.committer = committer
        self.message = message

    @property
    def header(self) -> str:
        """Constructs the header string containing object type and payload length.

        Returns:
            Formatted header string.
        """
        return f"commit {len(self.serialize_payload())}\n"

    def serialize_payload(self) -> bytes:
        """Serializes the commit contents including tree, parents, author, committer, and message.

        Returns:
            Encoded binary representation of the commit payload.
        """
        lines = [f"tree {self.tree}"]
        for parent in self.parent_hashes:
            lines.append(f"parent {parent}")
        lines.append(f"author {self.author} {self.timestamp}")
        lines.append(f"committer {self.committer} {self.timestamp}")
        lines.append("")
        lines.append(self.message)
        return "\n".join(lines).encode()

    def serialize(self) -> bytes:
        """Serializes the commit object by prepending the header and null byte to the payload.

        Returns:
            Full binary payload of the serialized commit object.
        """
        return f"{self.header}\x00".encode() + self.serialize_payload()
