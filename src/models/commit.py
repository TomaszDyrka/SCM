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

    @classmethod
    def deserialize(cls, data: bytes) -> "Commit":
        """Deserializes the commit object and creates new instance with the obtained data.

        Args:
            data: serialized commit in bytes.

        Returns:
            Deserialized commit.
        """
        _, payload = data.decode().split("\x00")
        clean_data = payload.split("\n")

        parent_hashes = []

        while line := clean_data.pop(0):
            pieces = line.split()
            match pieces[0]:
                case "tree":
                    # we need to take the second part for the tree
                    tree = pieces[1]

                case "parent":
                    # similar to the case above:
                    # we need to split then take the latter part
                    parent_hashes.append(pieces[1])

                case "author":
                    # for author we need to take everything between
                    # author and timestamp both ends exclusive
                    author = " ".join(pieces[1:-1:])

                case "committer":
                    # we take committer and timestamp together, as commiter
                    # SHOULD (hmmm?) be an email, probs, so one long string
                    # and two last bundled together

                    # as of now committer is just the same as author, so
                    # I will just copy that
                    committer = author
                    # committer = pieces[1]
                    timestamp = " ".join(pieces[-1::])

        message = "\n".join(clean_data)

        return cls(tree, parent_hashes, author, timestamp, committer, message)

    def __eq__(self, other: "Commit"):
        conditions = [
            self.tree == other.tree,
            sorted(self.parent_hashes) == sorted(other.parent_hashes),
            self.author == other.author,
            self.timestamp == other.timestamp,
            self.committer == other.committer,
            self.message == other.message,
        ]
        return all(conditions)
