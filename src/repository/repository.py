from pathlib import Path

class Repository:

    def __init__(self, repository_path: Path) -> None:
        hidden_folder_name = ".scm"

        self.repository_path = repository_path / hidden_folder_name
        self.objects = repository_path / hidden_folder_name / "objects"
        self.refs = repository_path / hidden_folder_name / "refs"
        self.HEAD = repository_path / hidden_folder_name / "HEAD.txt"

    def initialize_directories(self) -> None:
        self.objects.mkdir(parents=True, exist_ok=True)
        self.refs.mkdir(parents=True, exist_ok=True)

        if not self.HEAD.exists():
            self.HEAD.touch()