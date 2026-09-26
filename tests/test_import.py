"""Test todoist-scheduler."""

import todoist_scheduler


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(todoist_scheduler.__name__, str)


def test_version() -> None:
    """Test that the version is available."""
    assert isinstance(todoist_scheduler.__version__, str)
