import argparse

import pytest

from utils.parser.parser import BaseParser


@pytest.mark.parser
class TestCLIParser:
    """Main CLI tests"""

    def test_setup_cli_returns_base_parser(self, create_parser):
        """tests if setup_cli returns BaseParser"""
        parser = create_parser()
        assert isinstance(parser, BaseParser)

    def test_setup_cli_has_subparser_registry(self, create_parser):
        """tests if subparser_registry has been initialized"""
        parser = create_parser()
        assert hasattr(parser, "subparser_registry")


@pytest.mark.exampleCommand
class TestExampleCommand:
    """Tests use for ExampleCommand command"""

    def test_creation(self, example_command):
        """tests if ExampleCommand is written properly"""
        assert example_command._name != "base"
        assert not getattr(
            example_command.register_parser, "__isabstractmethod__", False
        )
        assert not getattr(example_command.execute, "__isabstractmethod__", False)

    def test_execute_with_valid_argument(self, example_command, capsys):
        """tests when flag 'test_arg' has flag 'y'."""
        mock_args = argparse.Namespace(test_pos_arg="y")
        # basicly string rn, should be changed later
        mock_repo = "RepoRepoBamBam"

        example_command.execute(mock_repo, mock_args)

        # caputre console output
        captured = capsys.readouterr()

        assert "RepoRepoBamBam" in captured.out
        # well, lets apporach it safely
        assert "args_worken!" in captured.out
        assert "nuh uh" not in captured.out

    def test_execute_with_invalid_argument(self, example_command, capsys):
        """tests when flag invalid"""
        mock_args = argparse.Namespace(test_pos_arg="nah")
        mock_repo = "RepoRepoBamBam"

        example_command.execute(mock_repo, mock_args)
        captured = capsys.readouterr()

        assert "RepoRepoBamBam" in captured.out
        assert "args_worken!" not in captured.out
        assert "nuh uh" in captured.out

    def test_execute_with_no_argument(self, example_command, capsys):
        """tests when no flag provided"""
        mock_args = argparse.Namespace()
        mock_repo = "RepoRepoBamBam"

        example_command.execute(mock_repo, mock_args)
        captured = capsys.readouterr()

        assert "RepoRepoBamBam" in captured.out
        assert "args_worken!" not in captured.out
        assert "nuh uh" in captured.out
