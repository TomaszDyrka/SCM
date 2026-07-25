from pathlib import Path
from unittest.mock import MagicMock
import argparse
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


def test_init_command_execute(tmp_path, monkeypatch):
    mock_repo_instance = MagicMock()
    mock_repo_class = MagicMock(return_value=mock_repo_instance)

    monkeypatch.setattr("commands.init.Repository", mock_repo_class)

    args = argparse.Namespace(path=tmp_path, branch_name="feature")

    InitCommand.execute(None, args)

    mock_repo_class.assert_called_once_with(tmp_path)
    mock_repo_instance.initialize_directories.assert_called_once()
    mock_repo_instance.update_head_path.assert_called_once_with("refs/heads/feature")