import os

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import click

from todoist_scheduler import cli


def job():
    """
    this is me being lazy, I don't want to have to define another entrypoint, so I'm just catching the successful outcome
    """
    try:
        cli()
    except click.exceptions.Exit as e:
        if e.exit_code != 0:
            raise


def cron():
    schedule = os.environ.get("SCHEDULE", "0 6 * * *")

    print(f"Running on schedule: {schedule}")

    scheduler = BlockingScheduler()
    scheduler.add_job(job, CronTrigger.from_crontab(schedule))
    scheduler.start()


if __name__ == "__main__":
    cron()
