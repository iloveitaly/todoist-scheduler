#!/usr/bin/env -S ipython -i

import os
from todoist_api_python.api import TodoistAPI

api_key = os.getenv("TODOIST_API_KEY")
api = TodoistAPI(api_key)