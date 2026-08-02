from pathlib import Path


def find_repository_root(start_path: Path | None = None) -> Path:
    current = (start_path or Path.cwd()).resolve()
    while current != current.parent:
        if (current / ".rvn").is_dir():
            return current / ".rvn"
        current = current.parent
    return (start_path or Path.cwd()) / ".rvn"