from pathlib import Path
from repository.repository import Repository
from utils.temp_cli import cli


def main():
    parser = cli.setup_cli()
    args = parser.main_parser.parse_args()

    if hasattr(args, "func"):
        repo = Repository(Path.cwd())
        args.func(repo, args)
    else:
        parser.main_parser.print_help()
        return


if __name__ == "__main__":
    main()
