import logging

import backoff
import requests
import todoist_api_python.http_requests

# backoff does not log by default
logging.getLogger("backoff").addHandler(logging.StreamHandler())


# https://github.com/Doist/todoist-api-python/issues/38
# backoff all non-200 errors
def patch_todoist_api():
    if hasattr(patch_todoist_api, "complete") and patch_todoist_api.complete:
        return

    patch_targets = ["delete", "get", "json", "post"]

    for target in patch_targets:
        original_function = getattr(todoist_api_python.http_requests, target)

        setattr(
            todoist_api_python.http_requests,
            f"original_{target}",
            original_function,
        )

        # TODO pretty sure authorization errors are retried :/

        def extract_retry_time(exception):
            """
            raw response on 429:

            b'{"error":"Too many requests. Limits reached. Try again later","error_code":35,"error_extra":{"event_id":"07c3fb965eaa4ec6a42e977c3e035c6b","retry_after":66},"error_tag":"LIMITS_REACHED","http_code":429}'
            """

            if (
                not isinstance(exception, requests.exceptions.HTTPError)
                or exception.response.status_code != 429
            ):
                raise exception

            retry_after_in_seconds = exception.response.json()["error_extra"][
                "retry_after"
            ]

            # add 10s of buffer
            return retry_after_in_seconds + 10

        patched_function = backoff.on_exception(
            backoff.runtime,
            (requests.exceptions.HTTPError),
            value=extract_retry_time,
            max_tries=8,
        )(original_function)

        patched_function2 = backoff.on_exception(
            backoff.expo,
            # RequestException superclass is IOError, which is a low-level py error
            # tried using HTTPError as the retry, but at scale the Todoist API has lots of interesting failures
            (requests.exceptions.RequestException),
            max_tries=30,
        )(patched_function)

        setattr(
            todoist_api_python.http_requests,
            target,
            patched_function2,
        )

    patch_todoist_api.complete = True


patch_todoist_api()
