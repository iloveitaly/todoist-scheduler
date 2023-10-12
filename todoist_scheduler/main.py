from todoist_api_python.api import TodoistAPI

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

    try:
        with socket.create_connection(("google.com", 80), timeout=5):
            return True
    except socket.error as e:
        return False


def _is_sunday():
    day_of_the_week = datetime.date.today().weekday()
    return day_of_the_week == 6


# TODO is this really needed given that this should run every day?
def _due_string(punt_time, jitter_days):
    if punt_time != "jitter":
        return punt_time

    random_days = random.randrange(jitter_days)
    return f"in {random_days} days"


# https://github.com/iloveitaly/todoist-api-python/commit/ec83531fae94a2ccd0a4bd6b2d1db95d86b129b6
def todoist_get_filters(api):
    from todoist_api_python.endpoints import get_sync_url
    from todoist_api_python.http_requests import post

    endpoint = get_sync_url("sync")
    data = {
        "resource_types": ["filters"],
        "sync_token": "*",
    }
    resource_data = post(api._session, endpoint, api._token, data=data)
    return resource_data


def _get_all_filters(api):
    response = todoist_get_filters(api)
    return {filter["name"]: filter["query"] for filter in response["filters"]}


def apply_todoist_filters(api_key, rules, task_limit, default_filter, **kwargs):
    if not _is_internet_connected():
        print("internet is not connected")
        return

    api = TodoistAPI(api_key)
    system_filters = _get_all_filters(api)

    for rule in rules:
        process_rule(
            api=api,
            rule=rule,
            default_filter=default_filter,
            system_filters=system_filters,
            **kwargs,
        )

    all_remaining_tasks = api.get_tasks(filter=default_filter)

    # let the user know they should incrementally improve their categorization so there's a reasonable number of tasks left
    if len(all_remaining_tasks) > task_limit:
        logger.warning("many remaining tasks left, improve filtering")


def process_rule(
    api, rule, dry_run, default_filter, system_filters, punt_time, jitter_days
):
    filter_with_label = f'{default_filter} & {rule["filter"]}'

    if rule["filter"] in system_filters:
        logger.debug("using system filter %s", rule["filter"])
        filter_with_label = f'{default_filter} & {system_filters[rule["filter"]]}'

    logger.debug(filter_with_label)

    tasks_with_label = api.get_tasks(filter=filter_with_label)

    # TODO should allow to be specified via CLI
    priority = 1

    # allow JSON to overwrite rules
    if "dry_run" in rule:
        dry_run = rule["dry_run"]
    if "punt_time" in rule:
        punt_time = rule["punt_time"]
    if "jitter_days" in rule:
        jitter_days = rule["jitter_days"]
    if "priority" in rule:
        priority = rule["priority"]

    # only reschedule low priority tasks; the API priorities are opposite from UI priorities
    # `Task priority from 1 (normal, default value) to 4 (urgent)`
    low_priority_tasks = [
        task for task in tasks_with_label if task.priority <= priority
    ]

    # randomize the task order so different tasks are displayed for completion each day
    random.shuffle(low_priority_tasks)

    # if sunday (day off) force limit of all non-essential tasks to zero
    limit_for_filter = 0 if _is_sunday() else rule["limit"]

    # after excluding the high-pri tasks, how many slots do we have left for this rule?
    remaining_tasks = limit_for_filter - (
        len(tasks_with_label) - len(low_priority_tasks)
    )
    logger.debug(f"{remaining_tasks} tasks remaining for {rule['filter']}")

    for low_priority_task in low_priority_tasks:
        if remaining_tasks <= 0:
            due_string = _due_string(punt_time, jitter_days)
            logger.info("punting task %s %s", low_priority_task.content, due_string)

            if not dry_run:
                api.update_task(low_priority_task.id, due_string=due_string)
        else:
            logger.debug("leaving task %s", low_priority_task.content)
            remaining_tasks -= 1
