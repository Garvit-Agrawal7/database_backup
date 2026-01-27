import pytest
from click.testing import CliRunner
from src.cli import cli

class TestCLI:

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_cli_version(self, runner):
        result = runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert 'Database Backup Utility' in result.output

    def test_cli_info(self, runner):
        result = runner.invoke(cli, ['info'])
        assert result.exit_code == 0
        assert 'MySQL' in result.output
        assert 'PostgreSQL' in result.output
        assert 'MongoDB' in result.output
        assert 'SQLite' in result.output

    def test_cli_help(self, runner):
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Usage:' in result.output

    def test_backup(self, runner):
        result = runner.invoke(cli, ['backup', '--help'])
        assert result.exit_code == 0
        assert 'backup' in result.output.lower()

    def test_restore(self, runner):
        result = runner.invoke(cli, ['restore', '--help'])
        assert result.exit_code == 0
        assert 'restore' in result.output.lower()
