from argparse import _SubParsersAction
from pathlib import Path

from colorama import init

from commands.base.base_command import BaseCommand
from models.commit import Commit
from models.tree import Tree
from repository.repository import Repository, get_file_mode

init(autoreset=True)


class CheckoutCommand(BaseCommand):
    _name = "checkout"

    @classmethod
    def register_parser(cls, registry: _SubParsersAction) -> None:
        """Registers parser with checkout command.
        Args:
            registry: main parser of the scm
        """
        subparser = registry.add_parser(cls._name)
        subparser.add_argument(
            "target",
            type=str,
            help="Target commit hash or branch name",
        )

        subparser.set_defaults(func=cls.execute)

    @staticmethod
    def execute(repo: Repository, args) -> None:
        """Reads contents of given commit and updates the files.
        Args:
            repo: repository on which command will be executed
            args: parsed command-line arguments containing options
        """
        
        try: 
            target_hash = repo.read_branch(args.target)
            is_detached_head = False
        except FileNotFoundError:
            target_hash = args.target
            is_detached_head = True
        
        if is_detached_head:
            repo.update_head_hash(target_hash)
        else:
            repo.update_head_path(args.target)
            
        target_commit = Commit.deserialize(repo.read_object(target_hash))
        tree_hash = target_commit.tree
        
        # so, we need to clean the current project directory tree in order to restore the target commit
        CheckoutCommand._clean_home_dir(repo, repo.repository_path.parent) 
        
        # and now we are restoring it
        with open(repo.index, "w") as index_file:
          CheckoutCommand._restore_tree(repo, tree_hash, repo.repository_path.parent, index_file)
        
        
    @classmethod
    def _restore_tree(cls, repo:Repository, tree_hash:str, current_path:Path, index_file:_io.TextIOWrapper) -> None:
        """Restores tree object to the working directory
        Args:
            repo: repository the command references
            tree_hash: current tree root
            current_path: path in which the changes will be done
            index_file: reference to index that will be updated with read blob-entries 
            
        """
        
        tree = Tree.deserialize(repo.read_object(tree_hash))
        
        # every entry in tree - if blob then write to file, if tree then unpack and iterate over
        for entry in tree.entries:
            match entry['type']:
                case 'tree':
                    new_path = current_path / entry['name']
                    new_path.mkdir(exist_ok=True)
                    cls._restore_tree(repo, entry['hash'], new_path, index_file)
                    
                case 'blob':
                    # could do it with decode(), however i would still need it to be in bytes (as it is faster - we skip encoding)
                    _, blob = repo.read_object(entry['hash']).split(b"\x00", 1)
                    file = current_path / entry['name']
                    
                    file.write_bytes(blob)
                    index_file.write(f"{get_file_mode(file)} {entry['hash']} {file.relative_to(repo.repository_path.parent).as_posix()}\n")
        
    @classmethod
    def _clean_home_dir(cls, repo:Repository, current_path:Path) -> None:
        """Cleans current dir structure before restoring target tree structure
        Args:
            repo: repository the command refernces
            current_path: path to the main folder where .rvn is located
        """
        current_index = repo.read_index()
        
        for path, _ in current_index.items():
            p = current_path / path 
            p.unlink(missing_ok=True)
            if p.parent != current_path and not any(p.parent.iterdir()):
                p.parent.rmdir()
            
            
    
