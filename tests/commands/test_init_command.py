import argparse
from pathlib import Path
from unittest.mock import MagicMock

from src.commands.commands.init_command import InitCommand


def test_init_command_register_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    InitCommand.register_parser(subparsers)

    args = parser.parse_args(["init", "-p", "custom/path", "-b", "main"])

    assert args.path == Path("custom/path")
    assert args.branch_name == "main"
    assert args.func == InitCommand.execute


def test_init_command_default_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    InitCommand.register_parser(subparsers)

    args = parser.parse_args(["init"])

    assert args.path == Path.cwd()
    assert args.branch_name == "master"


def test_init_command_execute(tmp_path, temp_repo):
    args = argparse.Namespace(path=tmp_path, branch_name="feature")

    temp_repo.initialize_directories = MagicMock()
    temp_repo.update_head_path = MagicMock()

    InitCommand.execute(temp_repo, args)

    assert (
        temp_repo.repository_path == tmp_path.resolve() / temp_repo.hidden_folder_name
    )
    temp_repo.initialize_directories.assert_called_once()
    temp_repo.update_head_path.assert_called_once_with("feature")
