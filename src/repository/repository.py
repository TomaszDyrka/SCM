from pathlib import Path
import hashlib
from zlib import compress, decompress


def compute_hash(content: bytes) -> str:
    return hashlib.sha1(content).hexdigest()

class Repository:

    # Initialization
    def __init__(self, repository_path: Path) -> None:
        hidden_folder_name = ".scm"

        self.repository_path = repository_path / hidden_folder_name
        self.objects = repository_path / hidden_folder_name / "objects"
        self.refs = repository_path / hidden_folder_name / "refs"
        self.HEAD = repository_path / hidden_folder_name / "HEAD.txt"

    def initialize_directories(self) -> None:
        self.objects.mkdir(parents=True, exist_ok=True)
        self.refs.mkdir(parents=True, exist_ok=True)
        heads = self.refs / "heads"
        heads.mkdir(parents=True, exist_ok=True)

        if not self.HEAD.exists():
            self.HEAD.touch()

    # Writing Methods
    def write_object(self, content: bytes) -> str:
        # Determine paths
        object_hash = compute_hash(content)
        folder_name, file_name = object_hash[:2], object_hash[2:]
        folder_path = self.objects / folder_name
        file_path = folder_path / file_name

        # Create structure
        folder_path.mkdir(parents=False, exist_ok=True)

        # Write content
        compressed_content = compress(content)
        with open(file=file_path, mode="wb") as object_file:
            object_file.write(compressed_content)

        return object_hash

    def update_branch(self, name: str, last_commit_metadata: str):
        commit_hash = compute_hash(last_commit_metadata.encode())
        file_path = self.refs / "heads" / name

        with open(file=file_path, mode="w") as head_file:
            head_file.write(commit_hash)

        return commit_hash

    def update_head_path(self, branch_name: str) -> None:
        content = f"ref: refs/heads/{branch_name}"

        with open(file=self.HEAD, mode="w") as head_file:
            head_file.write(content)

    def update_head_hash(self, commit_hash: str) -> None:

        with open(file=self.HEAD, mode="w") as head_file:
            head_file.write(commit_hash)