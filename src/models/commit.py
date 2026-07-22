class Commit:
    def __init__(self,
                 tree: str,
                 parent_hashes: list[str],
                 author: str,
                 timestamp: str,
                 committer: str,
                 message: str) -> None:

        self.tree = tree
        self.parent_hashes = parent_hashes
        self.author = author
        self.timestamp = timestamp
        self.committer = committer
        self.message = message

    @property
    def header(self) -> str:
        return f"commit {len(self.serialize_payload())}"

    def serialize_payload(self) -> bytes:
        lines = [f"tree {self.tree}"]
        for parent in self.parent_hashes:
            lines.append(f"parent {parent}")
        lines.append(f"author {self.author} {self.timestamp}")
        lines.append(f"committer {self.committer} {self.timestamp}")
        lines.append("")
        lines.append(self.message)
        return "\n".join(lines).encode()

    def serialize(self) -> bytes:
        return f"{self.header}\x00".encode() + self.serialize_payload()