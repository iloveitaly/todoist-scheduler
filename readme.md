# Todoist Task Scheduler & Filterer

I've been experimenting with my productivity systems. I'm a heavy user of [Todoist](http://mikebian.co/todoist) and I noticed that:

1. If I have a smaller list of tasks to accomplish, I get through them faster.
2. Having a large list of tasks creates 'cognitive drag' and stresses me out
3. It takes time to look through and review long list of tasks

This simple tool enables you to set up rules to automatically punt tasks that don't need to get done today. This reduces the size of your todoist and tricks you monkey mind into getting more done. The ultimate goal for me is to get to 'inbox zero' on todoist which is something that hasn't happened in years.

## Usage

```
Usage: todoist-scheduler [OPTIONS]

  Organizes todoist tasks based on custom rules

Options:
  --task-limit INTEGER   Total task limit for the day  [default: 20]
  --default-filter TEXT  Default todoist filter  [default: (today | overdue) &
                         !assigned to:others & !recurring]
  --filter-json TEXT     Default todoist filter  [default: filters.json]
  --punt-time TEXT       Default time to punt a task into the future
                         [default: in 2 days]
  --dry-run              Dry run the task updates
  --api-key TEXT         API key. Sourced from TODOIST_API_KEY as well
  --help                 Show this message and exit.
```

Take a closer look at the default filter:

```
default: (today | overdue) & !assigned to:others & !recurring
```

Here's what this does:

* Only applies filters to task that are assigned to you
* Ignores recurring tasks
* Looks at tasks due on or before today

#### filters.json

```json
[
  // limit defines the number of tasks you think you can complete today
  { "filter": "@writing", "limit": 2 },
  { "filter": "@research", "limit": 3 },

  // the filter text uses the todoist search syntax
  { "filter": "#House", "limit": 3 },
]
```