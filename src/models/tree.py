class Tree:
    def __init__(self) -> None:
        self.entries = []

    def add_entry(self,
                  entry_hash: str,
                  entry_type: str,
                  entry_name: str) -> None:

        self.entries.append({"hash": entry_hash,
                             "type": entry_type,
                             "name": entry_name})

    @property
    def header(self) -> str:
        return f"tree {len(self.serialize_payload())}"

    def serialize_payload(self) -> bytes:
        rows = [f"{row['type']} {row['hash']} {row['name']}" for row in self.entries]
        return "\n".join(rows).encode()

    def serialize(self) -> bytes:
        return f"{self.header}\x00".encode() + self.serialize_payload()
