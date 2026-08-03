from argparse import _SubParsersAction
from datetime import datetime
from pathlib import Path
from difflib import unified_diff

from colorama import Style, init

from commands.base.base_command import DEEP_PURPLE, DEEP_RED, BaseCommand, CLIOutput
from errors.errors import RepositoryNotInitializedError, StagingAreaDoesNotExistError
from models.commit import Commit

from models.tree import Tree

init(autoreset=True)

messages = {
    "successful_commit_branch": lambda branch, message: (
        f"Successfully commited to the branch [{DEEP_PURPLE}{branch}{Style.RESET_ALL}] {message}"
    ),
    "error_no_staging_area": f"No file has been added yet. Use {DEEP_RED}rvn add{Style.RESET_ALL} and try again.",
    "repo_not_initialized": f"Repository has not been initialized yet. Use {DEEP_RED}rvn init{Style.RESET_ALL} and try again.",
}


class CommitCommand(BaseCommand):
    _name = "commit"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers the commit command parser with available arguments and flags.

        Args:
            registry: Subparser action manager where the command will be registered.
        """
        subparser = registry.add_parser(cls._name)
        subparser.add_argument(
            "message",
            type=str,
            help="Commit message.",
        )

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo, args) -> None:
        """Executes the commit command.

        Args:
            repo: Repository instance on which the command will be executed.
            args: Parsed command-line arguments containing options.
        """
        try:
            if not repo.index.exists():
                raise StagingAreaDoesNotExistError("No file has been added yet. Use rvn add and try again.")

            is_detached_head = False
            tree_hash = CommitCommand._create_tree_structure(repo)
            parent_hash_list = []
            branch_name = ""

            if repo.read_head().split(" ", 1)[0] == "ref:":
                branch_name = Path(repo.read_head().split(" ", 1)[1]).name
                try:
                    parent_hash_list = [repo.read_branch(branch_name)]
                except FileNotFoundError:
                    pass
            else:
                parent_hash_list = [repo.read_head()]
                is_detached_head = True

            new_commit = Commit(tree_hash, parent_hash_list, "Revan", CommitCommand._get_timestamp(), "Revan", args.message)
            commit_hash = repo.write_object(new_commit.serialize())

            if not is_detached_head:
                repo.update_branch(branch_name, commit_hash)
                CLIOutput.info(messages["successful_commit_branch"](branch_name, args.message))
            else:
                repo.update_head_hash(commit_hash)
        except RepositoryNotInitializedError:
            CLIOutput.error(messages["repo_not_initialized"])
        except StagingAreaDoesNotExistError:
            CLIOutput.error(messages["error_no_staging_area"])


    @staticmethod
    def _create_tree_structure(repo) -> str:
        index_content = repo.read_index()

        # Get all the unique folder paths from the staging area (index.txt)
        catalogs = set()
        for record in index_content:
            file_path = Path(record.split(" ")[-1])
            catalogs.update(file_path.parents)

        sorted_catalogs = sorted(catalogs, key=lambda x: len(x.parts), reverse=True)

        # Create Tree and BLOB objects
        trees_created = {}
        for catalog in sorted_catalogs:
            new_tree = Tree()

            for record in index_content.values():
                hash_value, path_str = record.hash, record.path
                path = Path(path_str)

                # Adding BLOBs to Tree structure
                if path.parent == catalog:
                    new_tree.add_entry(hash_value, "blob", path.name)

            # Adding sub-Trees to Tree structure
            for child_catalog, child_tree_hash in trees_created.items():
                if child_catalog.parent == catalog:
                    new_tree.add_entry(child_tree_hash, "tree", child_catalog.name)

            # Adding this iteration's Tree
            trees_created[catalog] = repo.write_object(new_tree.serialize())

        # Returning project's hash
        return trees_created[Path(".")]

    @staticmethod
    def _get_timestamp() -> str:
        now = datetime.now().astimezone()
        seconds = int(now.timestamp())
        tz_offset = now.strftime("%z")
        return f"{seconds} {tz_offset}"
