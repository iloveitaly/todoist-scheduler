import os

import click
import pyjson5 as json  # allows comments in json

from todoist_scheduler import main


@click.group()
@click.option(
    "--dry-run",
    default=False,
    help="Dry run the task updates",
    show_default=True,
    type=bool,
    is_flag=True,
)
@click.option(
    "--api-key",
    default=os.getenv("TODOIST_API_KEY"),
    help="API key. Sourced from TODOIST_API_KEY too.",
)
@click.pass_context
def cli(ctx, dry_run, api_key):
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["api_key"] = api_key


@cli.command(help="Organizes todoist tasks based on custom rules")
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
    help="Default filter file",
    show_default=True,
    type=click.Path(exists=True),
)
@click.option(
    "--punt-time",
    default="in 2 days",
    help="How far to punt a task into the future. Use todoist natural language format. The special value 'jitter' will generate a random date.",
    show_default=True,
    type=str,
)
@click.option(
    "--jitter-days",
    default="14",
    help="What day range to jitter tasks across when rescheduling them",
    show_default=True,
    type=int,
)
@click.pass_context
def organize_tasks(ctx, **kwargs):
    if not ctx.obj["api_key"]:
        raise click.ClickException("No API key found")

    with open(kwargs["filter_json"]) as f:
        kwargs["rules"] = json.load(f)

    del kwargs["filter_json"]

    kwargs["dry_run"] = ctx.obj["dry_run"]
    kwargs["api_key"] = ctx.obj["api_key"]

    main.apply_todoist_filters(**kwargs)


@cli.command(help="Removes tasks older than 180 days with dead links")
@click.pass_context
def remove_dead_link_tasks(ctx):
    if not ctx.obj["api_key"]:
        raise click.ClickException("No API key found")

    main.remove_dead_link_tasks(dry_run=ctx.obj["dry_run"], api_key=ctx.obj["api_key"])


if __name__ == "__main__":
    cli()
