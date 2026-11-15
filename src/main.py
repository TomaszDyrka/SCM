from repository.find_root import find_repository_root
from repository.repository import Repository
from utils.temp_cli import cli


def main():
    parser = cli.setup_cli()
    args = parser.main_parser.parse_args()

    if hasattr(args, "func"):
        repo = Repository(find_repository_root().parent)
        args.func(repo, args)
    else:
        parser.main_parser.print_help()
        return


if __name__ == "__main__":
    main()
