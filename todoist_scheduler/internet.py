"""
I have this running on a orangepi in my home, and my eero has been disconnecting from the internet
overnight. This makes sure that an intermittent internet failure doesn't cause the job not to run.
"""

import socket

import backoff

# 8 hours, in case the internet goes down overnight
MAX_WAIT_TIME = 60 * 60 * 8


class InternetConnectionError(Exception):
    pass


@backoff.on_exception(backoff.expo, InternetConnectionError, max_time=MAX_WAIT_TIME)
def wait_for_internet_connection():
    if is_internet_connected():
        return

    raise InternetConnectionError("no internet connection")


def is_internet_connected():
    try:
        with socket.socket(socket.AF_INET) as s:
            s.connect(("google.com", 80))
            return True
    except OSError:
        return False
