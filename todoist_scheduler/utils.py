"""
This file should be imported first in any application entrypoint.
"""

import logging
import typing as t
from pathlib import Path

import structlog
from decouple import config

root: Path

# must type manually, unfortunately :/
# https://www.structlog.org/en/21.3.0/types.html
log: structlog.stdlib.BoundLogger


def configure_logger():
    global log

    # context manager to auto-clear context
    log.context = structlog.contextvars.bound_contextvars  # type: ignore
    # set thread-local context
    log.local = structlog.contextvars.bind_contextvars  # type: ignore
    # clear thread-local context
    log.clear = structlog.contextvars.clear_contextvars  # type: ignore

    logger_factory = structlog.PrintLoggerFactory()

    # allow user to specify a log in case they want to do something meaningful with the stdout
    if python_log_path := config("PYTHON_LOG_PATH", default=None):
        python_log = open(
            python_log_path, "a", encoding="utf-8"
        )  # pylint: disable=consider-using-with
        logger_factory = structlog.PrintLoggerFactory(file=python_log)

    log_level = t.cast(str, config("LOG_LEVEL", default="INFO", cast=str))
    level = getattr(logging, log_level.upper())

    # TODO logging.root.manager.loggerDict
    # we need this option to be set for other non-structlog loggers
    logging.basicConfig(level=level)

    # TODO look into further customized format
    # https://cs.github.com/GeoscienceAustralia/digitalearthau/blob/4cf486eb2a93d7de23f86ce6de0c3af549fe42a9/digitalearthau/uiutil.py#L45

    structlog.configure(
        context_class=dict,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=logger_factory,
        cache_logger_on_first_use=True,
    )


def setup():
    if hasattr(setup, "complete") and setup.complete:
        return

    global root, log

    root = Path(__file__).parent.parent

    log = structlog.get_logger()
    configure_logger()

    log.debug("application setup")

    # local state in a method is strange, but it works :/
    setup.complete = True


# side effects are bad, but it's fun to do bad things
setup()
