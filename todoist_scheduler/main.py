from todoist_api_python.api import TodoistAPI

# cleanup ugly ipython backtraces
# https://cs.github.com/ipython/ipython/blob/46a51ed69cdf41b4333943d9ceeb945c4ede5668/IPython/core/crashhandler.py#L225
import IPython.core.crashhandler

IPython.core.crashhandler.crash_handler_lite = lambda one, two, three: None

import random
import datetime
import logging, os

logger = logging.getLogger(__name__)
logging.basicConfig(
    datefmt="%m-%d %H:%M", format="%(asctime)s %(levelname)-8s %(message)s"
)

# run with LOG_LEVEL=DEBUG
# https://stackoverflow.com/questions/11548674/logging-info-doesnt-show-up-on-console-but-warn-and-error-do
log_level = os.environ.get("LOG_LEVEL", "INFO")
logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

def _is_internet_connected():
    import socket
    s = socket.socket(socket.AF_INET)
    try:
        s.connect(("google.com",80))
        return True
    except socket.error as e: return False

def _is_sunday():
    day_of_the_week = datetime.date.today().weekday()
    return day_of_the_week == 6

def _random_date_in_next_days(days=14):
    today = datetime.date.today()
    days_delta = datetime.timedelta(days=days)
    random_day = random.randrange(days_delta.days)
    return today + datetime.timedelta(days=random_day)

def apply_todoist_filters(
    task_limit, api_key, rules, dry_run, punt_time, default_filter
):
    if not _is_internet_connected():
        print("internet is not connected")
        return

    # defaults are applied here in case None values are passed to the kwargs from click

    if not default_filter:
        default_filter = "(today | overdue) & !assigned to:others & !recurring"

    if not punt_time:
        punt_time = "in 2 days"

    api = TodoistAPI(api_key)
    is_sunday = _is_sunday()

    for rule in rules:
        filter_with_label = f'{default_filter} & {rule["filter"]}'
        logger.debug(filter_with_label)

        tasks_with_label = api.get_tasks(filter=filter_with_label)

        # only reschedule low priority tasks; the API priorities are opposite from UI priorities
        # `Task priority from 1 (normal, default value) to 4 (urgent)`
        low_priority_tasks = [task for task in tasks_with_label if task.priority == 1]

        # randomize the task order so different tasks are displayed for completion each day
        random.shuffle(low_priority_tasks)

        # TODO should allow this to be customized
        # if sunday (day off) force limit of all non-essential tasks to zero
        limit_for_filter = 0 if is_sunday else rule["limit"]

        # after excluding the high-pri tasks, how many slots do we have left for this rule?
        remaining_tasks = limit_for_filter - (
            len(tasks_with_label) - len(low_priority_tasks)
        )
        logger.debug(f"{remaining_tasks} tasks remaining for {rule['filter']}")

        for low_priority_task in low_priority_tasks:
            if remaining_tasks <= 0:
                logger.info("punting task %s", low_priority_task.content)

                if not dry_run:
                    api.update_task(low_priority_task.id, due_string=punt_time)
            else:
                logger.debug("leaving task %s", low_priority_task.content)
                remaining_tasks -= 1

    all_remaining_tasks = api.get_tasks(filter=default_filter)

    # let the user know they should incrementally improve their categorization so there's a reasonable number of tasks left
    if len(all_remaining_tasks) > task_limit:
        logger.warn("many remaining tasks left, improve filtering")
