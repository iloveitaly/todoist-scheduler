from .cli import cli
from .version import __version__

main = cli

__all__ = ["__version__", "cli", "main"]
