from click.testing import CliRunner

from todoist_scheduler import cli
from todoist_scheduler.internet import is_internet_connected
from todoist_scheduler.main import _due_string, _is_sunday
from todoist_scheduler.utils import setup


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Organizes todoist tasks based on custom rules" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_cli_no_api_key(tmp_path):
    dummy_filter = tmp_path / "filters.json"
    dummy_filter.write_text("[]")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--api-key", "", "--filter-json", str(dummy_filter)],
        env={"TODOIST_API_KEY": ""},
    )
    assert result.exit_code != 0
    assert "No API key found" in result.output


def test_cli_missing_filter_file(tmp_path):
    runner = CliRunner()
    missing_file = tmp_path / "nonexistent.json"
    result = runner.invoke(
        cli,
        ["--api-key", "test", "--filter-json", str(missing_file)],
    )
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_due_string():
    assert _due_string("tomorrow", 14) == "tomorrow"
    jitter = _due_string("jitter", 5)
    assert jitter.startswith("in ") and jitter.endswith(" days")


def test_is_sunday():
    assert isinstance(_is_sunday(), bool)


def test_is_internet_connected():
    result = is_internet_connected()
    assert isinstance(result, bool)


def test_utils_setup():
    setup()
