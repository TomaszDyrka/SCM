import pytest
import argparse

from utils.temp_cli.cli import setup_cli
from utils.parser.parser import BaseParser
from commands.commands.example_command import ExampleCommand

class TestCLIParser:
    """Main CLI tests"""

    def test_setup_cli_returns_base_parser(self):
        """tests if setup_cli returns BaseParser"""

        parser = setup_cli()
        print(type(parser).__module__)
        print(BaseParser.__module__)
        assert isinstance(parser, BaseParser)
        
    def test_setup_cli_has_subparser_registry(self):
        """tests if subparser_registry has been initialized"""

        parser = setup_cli()
        assert hasattr(parser, 'subparser_registry')


class TestExampleCommand:
    """Tests use for ExampleCommand command"""

    def test_creation(self, capsys):
        """tests if ExampleCommand is written properly"""
        assert ExampleCommand._name != "base"
        assert not getattr(ExampleCommand.register_parser, "__isabstractmethod__", False)
        assert not getattr(ExampleCommand.execute, "__isabstractmethod__", False)

    def test_execute_with_valid_argument(self, capsys):
        """tests when flag 'test_arg' has flag 'y'."""

        mock_args = argparse.Namespace(test_pos_arg="y")
        # basicly string rn, should be changed later
        mock_repo = "RepoRepoBamBam"
        
        ExampleCommand.execute(mock_repo, mock_args)
        
        # caputre console output
        captured = capsys.readouterr()
        
        assert "RepoRepoBamBam" in captured.out
        # well, lets apporach it safely
        assert "args_worken!" in captured.out
        assert "nuh uh" not in captured.out

    def test_execute_with_invalid_argument(self, capsys):
        """tests when flag invalid"""

        mock_args = argparse.Namespace(test_pos_arg="nah")
        mock_repo = "RepoRepoBamBam"
        
        ExampleCommand.execute(mock_repo, mock_args)
        captured = capsys.readouterr()
        
        assert "RepoRepoBamBam" in captured.out
        assert "args_worken!" not in captured.out
        assert "nuh uh" in captured.out

    def test_execute_with_no_argument(self, capsys):
        """tests when no flag provided"""

        mock_args = argparse.Namespace()
        mock_repo = "RepoRepoBamBam"
        
        ExampleCommand.execute(mock_repo, mock_args)
        captured = capsys.readouterr()
        
        assert "RepoRepoBamBam" in captured.out
        assert "args_worken!" not in captured.out
        assert "nuh uh" in captured.out
