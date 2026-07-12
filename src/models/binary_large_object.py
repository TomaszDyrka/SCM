class BinaryLargeObject:
    def __init__(self, content: bytes) -> None:
        self.content = content

    @property
    def header(self) -> str:
        return f"blob {len(self.content)}"

    def serialize(self) -> bytes:
        return f"{self.header}\x00".encode() + self.content