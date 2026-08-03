import os
from argparse import _SubParsersAction
from pathlib import Path

from colorama import Style, init

from commands.base.base_command import DEEP_PURPLE, BaseCommand, CLIOutput
from models.binary_large_object import BinaryLargeObject

from models.tree import Tree

init(autoreset=True)

# messages = {
#     "success": lambda path, branch_name: (
#         f"Successfully initialized RVN repository at {DEEP_PURPLE}{path}{Style.RESET_ALL} "
#         f"with {DEEP_PURPLE}{branch_name}{Style.RESET_ALL} as its main branch."
#     )
# }


class CommitCommand(BaseCommand):
    _name = "commit"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers the init command parser with available arguments and flags.

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
        print(f"Commited {args.message}")
        CommitCommand._create_tree_structure(repo)

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

            for record in index_content:
                mode, hash_value, path_str = record.split(" ")
                path = Path(path_str)

                # Adding BLOBs to Tree structure
                if path.parent == catalog:
                    new_tree.add_entry(hash_value, "blob", path.name)

            # Adding sub-Trees to Tree structure
            for child_catalog, child_tree_hash in trees_created.items():
                if child_catalog.parent == catalog:
                    new_tree.add_entry(child_tree_hash, "tree", child_catalog.name)

            # Adding this iteration's Tree
            trees_created[catalog] = repo.write_object(new_tree)

        # Returning project's hash
        return trees_created[Path(".")]
