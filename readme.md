[![Release Notes](https://img.shields.io/github/release/iloveitaly/todoist-scheduler)](https://github.com/iloveitaly/todoist-scheduler/releases) [![Downloads](https://static.pepy.tech/badge/todoist-scheduler/month)](https://pepy.tech/project/todoist-scheduler) [![Python Versions](https://img.shields.io/pypi/pyversions/todoist-scheduler)](https://pypi.org/project/todoist-scheduler) ![GitHub CI Status](https://github.com/iloveitaly/todoist-scheduler/actions/workflows/build_and_publish.yml/badge.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Todoist Task Scheduler & Filterer

I'm a heavy user of [Todoist](http://mikebian.co/todoist) and I noticed that:

1. If I have a smaller list of tasks to accomplish, I get through them faster.
2. Having a large list of tasks creates 'cognitive drag' and stresses me out
3. It takes time to look through and review long list of tasks

This simple tool enables you to set up rules to automatically punt tasks that don't need to get done today. This reduces the size of your todoist and tricks you monkey mind into getting more done. The ultimate goal for me is to get to 'inbox zero' on todoist which is something that hasn't happened in years.

## Usage

```text
Usage: todoist-scheduler [OPTIONS]

  Organizes todoist tasks based on custom rules

Options:
  --task-limit INTEGER   Total task limit for the day  [default: 20]
  --default-filter TEXT  Default todoist filter  [default: (today | overdue) &
                         !assigned to:others & !recurring]
  --filter-json TEXT     Default filter file  [default: filters.json]
  --punt-time TEXT       How far to punt a task into the future. Use todoist
                         natural language format. The special value 'jitter'
                         will generate a random date.  [default: in 2 days]
  --jitter-days INTEGER  What day range to jitter tasks across when
                         rescheduling them  [default: 14]
  --dry-run              Dry run the task updates
  --api-key TEXT         API key. Sourced from TODOIST_API_KEY as well
  --help                 Show this message and exit.
```

Take a closer look at the default filter:

```text
default: (today | overdue) & !assigned to:others & !recurring
```

Here's what this does:

* Only applies filters to task that are assigned to you
* Ignores recurring tasks
* Looks at tasks due on or before today

#### filters.json schema

```json5
[
  // limit defines the number of tasks you think you can complete today
  { "filter": "@writing", "limit": 2 },
  { "filter": "@research", "limit": 3 },

  // the filter text uses the todoist search syntax
  { "filter": "#House", "limit": 3 },
]
```

The JSON file is loaded in as [JSON5](https://json5.org) so you can add comments.

You can also override options for specific entries and reference saved/named filters:

```json5
[
  // loosen the priority filter
  { "filter": "@writing", "limit": 2, "priority": 2 },

  // reference a saved filter
  { "filter": "Communication", "limit": 3 },
]
```

## Development

Run with debug logging:

```shell
LOG_LEVEL=DEBUG todoist-scheduler
```

Play with the Todoist API (in `ipython`):

```python
from todoist_api_python.api import TodoistAPI
import os
api = TodoistAPI(os.getenv("TODOIST_API_KEY"))
```

Note that `ipython` is not included in the repo, [I install all my debugging tools via this alias](https://github.com/iloveitaly/dotfiles/blob/e41a309b0ca1f5099bc6d902d0956ba0fc997db1/.aliases#L76-L77) instead of including them in the poetry config.
