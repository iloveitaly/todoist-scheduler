import os

import click
from dotenv import load_dotenv
import pyjson5 as json  # allows comments in json
import main

load_dotenv()


@click.command(help="Organizes todoist tasks based on custom rules")
@click.option(
    "--task-limit",
    default=20,
    help="Total task limit for the day",
    show_default=True,
    type=int,
)
@click.option(
    "--default-filter",
    default="(today | overdue) & !assigned to:others & !recurring",
    help="Default todoist filter",
    show_default=True,
    type=str,
)
@click.option(
    "--filter-json",
    default="filters.json",
    help="Default todoist filter",
    show_default=True,
    type=str,
)
@click.option(
    "--punt-time",
    default="in 2 days",
    help="Default time to punt a task into the future",
    show_default=True,
    type=str,
)
@click.option(
    "--dry-run",
    default=False,
    help="Dry run the task updates",
    show_default=True,
    type=bool,
    is_flag=True,
)
@click.option(
    "--api-key", default=None, help="API key. Sourced from TODOIST_API_KEY as well"
)
def cli(**kwargs):
    if not kwargs["api_key"]:
        kwargs["api_key"] = os.getenv("TODOIST_API_KEY")

    if not kwargs["api_key"]:
        raise click.ClickException("No API key found")

    with open(kwargs["filter_json"]) as f:
        kwargs["rules"] = json.load(f)

    del kwargs["filter_json"]

    main.apply_todoist_filters(**kwargs)


if __name__ == "__main__":
    cli()
