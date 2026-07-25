import os
from pathlib import Path
import hashlib
from zlib import compress, decompress

from models.binary_large_object import BinaryLargeObject
from .ensure_initialized_wrapper import ensure_initialized
from dataclasses import dataclass


@dataclass
class IndexEntry:
    mode: str
    hash: str
    path: str

def compute_hash(content: bytes) -> str:
    """Computes the SHA-1 hash for the given binary content.

    Args:
        content: Binary content to hash.

    Returns:
        Hexadecimal representation of the computed SHA-1 hash.
    """
    return hashlib.sha1(content).hexdigest()

class Repository:
    """Manages the structure, files, and objects of a repository."""

    # Initialization
    def __init__(self, repository_path: Path) -> None:
        """Initializes the repository instance with target paths.

        Args:
            repository_path: Path where the repository is located or created.
        """
        self.hidden_folder_name = ".rvn"

        self.repository_path = None
        self.objects = None
        self.refs = None
        self.HEAD = None
        self.index = None
        self.set_repository_path(repository_path)

        self._directories_initialized = False

    def set_repository_path(self, repository_path: Path) -> None:
        """Sets internal directory and file paths based on the repository location.

        Args:
            repository_path: Target root directory for the repository.
        """
        self.repository_path = repository_path / self.hidden_folder_name
        self.objects = repository_path / self.hidden_folder_name / "objects"
        self.refs = repository_path / self.hidden_folder_name / "refs"
        self.HEAD = repository_path / self.hidden_folder_name / "HEAD.txt"
        self.index = repository_path / self.hidden_folder_name / "index.txt"

    def initialize_directories(self) -> None:
        """Creates the required repository directories and HEAD file on disk."""
        self.objects.mkdir(parents=True, exist_ok=True)
        self.refs.mkdir(parents=True, exist_ok=True)
        heads = self.refs / "heads"
        heads.mkdir(parents=True, exist_ok=True)

        if not self.HEAD.exists():
            self.HEAD.touch()

        self._directories_initialized = True

    # Writing Methods
    @ensure_initialized
    def write_object(self, content: bytes) -> str:
        """Compresses and writes binary content to the objects directory.

        Args:
            content: Binary content of the object to store.

        Returns:
            Computed SHA-1 hash of the stored object.
        """
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

    @ensure_initialized
    def update_branch(self, name: str, last_commit_metadata: str):
        """Updates or creates a branch reference with a new commit hash.

        Args:
            name: Name of the branch to update.
            last_commit_metadata: Commit metadata used to calculate hash.

        Returns:
            Computed hash of the commit written to the branch.
        """
        commit_hash = compute_hash(last_commit_metadata.encode())
        file_path = self.refs / "heads" / name

        with open(file=file_path, mode="w") as head_file:
            head_file.write(commit_hash)

        return commit_hash

    @ensure_initialized
    def update_head_path(self, branch_name: str) -> None:
        """Updates HEAD to point to a specific branch reference.

        Args:
            branch_name: Target branch name.
        """
        content = f"ref: refs/heads/{branch_name}"

        with open(file=file_path if (file_path := self.HEAD) else self.HEAD, mode="w") as head_file:
            head_file.write(content)

    @ensure_initialized
    def update_head_hash(self, commit_hash: str) -> None:
        """Updates HEAD directly with a commit hash (detached HEAD state).

        Args:
            commit_hash: Commit hash to set directly in HEAD.
        """
        with open(file=self.HEAD, mode="w") as head_file:
            head_file.write(commit_hash)

    @ensure_initialized
    def add_file_to_index(self, file_path: Path, blob: BinaryLargeObject) -> None:
        """Adds or updates a file entry in the repository index.

        Args:
            file_path: Path of the file relative to the repository root.
            blob: Serialized binary large object representing the file content.
        """
        file_mode = file_path.stat().st_mode
        blob_hash = compute_hash(blob.serialize())
        relative_path = file_path.relative_to(self.repository_path.parent)

        # Get all entries from index.txt
        entries = {}
        if self.index.exists():
            with open(file=self.index, mode="r") as index_file:
                for line in index_file:
                    if line.strip():
                        mode, b_hash, path = line.strip().split(" ", 2)
                        entries[path] = (mode, b_hash)

        # Add/Update entry
        entries[str(relative_path)] = (file_mode, blob_hash)

        # Recreate index.txt with changes
        with open(file=self.index, mode="w") as index_file:
            for path, (mode, b_hash) in entries.items():
                index_file.write(f"{mode} {b_hash} {path}\n")

    # Reading Methods
    @ensure_initialized
    def read_object(self, object_hash: str) -> bytes:
        """Reads and decompresses an object from the objects directory.

        Args:
            object_hash: SHA-1 hash identifier of the object.

        Returns:
            Decompressed binary content of the requested object.

        Raises:
            FileNotFoundError: If no object with the given hash exists.
        """
        # Determine paths
        folder_name, file_name = object_hash[:2], object_hash[2:]
        folder_path = self.objects / folder_name
        file_path = folder_path / file_name

        if not file_path.exists():
            raise FileNotFoundError(f"Object {object_hash} does not exist in the repository.")

        # Read and decompress object's content
        with open(file=file_path, mode="rb") as object_file:
            compressed_content = object_file.read()

        decompressed_content = decompress(compressed_content)

        return decompressed_content

    @ensure_initialized
    def read_branch(self, name: str) -> str:
        """Reads the commit hash referenced by a branch.

        Args:
            name: Name of the branch.

        Returns:
            Commit hash saved in the branch reference file.

        Raises:
            FileNotFoundError: If the requested branch reference does not exist.
        """
        file_path = self.refs / "heads" / name

        if not file_path.exists():
            raise FileNotFoundError(f"Branch {name} does not exist in the repository.")

        with open(file=file_path, mode="r") as head_file:
            commit_hash = head_file.read().strip()

        return commit_hash

    @ensure_initialized
    def read_head(self) -> str:
        """Reads raw content of the HEAD file.

        Returns:
            Content of the HEAD file.
        """
        with open(file=self.HEAD, mode="r") as head_file:
            head_content = head_file.read()

        return head_content

    @ensure_initialized
    def read_index(self) -> dict[str, IndexEntry]:
        """Reads and parses the repository index file.

        Returns:
            A dictionary mapping relative file paths to their corresponding IndexEntry objects.
        """
        entries = {}
        if self.index.exists():
            with open(file=self.index, mode="r") as index_file:
                for line in index_file:
                    line = line.strip()
                    if line:
                        mode, b_hash, path = line.split(" ", 2)
                        entries[path] = IndexEntry(mode=mode, hash=b_hash, path=path)

        return entries
