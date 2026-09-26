import json
import logging

import backoff
import httpx
from todoist_api_python._core import http_requests

# backoff does not log by default
logging.getLogger("backoff").addHandler(logging.StreamHandler())


# https://github.com/Doist/todoist-api-python/issues/38
# backoff 429 rate limit and server/network errors
def patch_todoist_api():
    if getattr(patch_todoist_api, "complete", False):
        return

    patch_targets = ["delete", "get", "post"]

    for target in patch_targets:
        original_function = getattr(http_requests, target)

        setattr(
            http_requests,
            f"original_{target}",
            original_function,
        )

        def extract_retry_time(exception: httpx.HTTPStatusError) -> float:
            """
            raw response on 429:

            b'{"error":"Too many requests. Limits reached. Try again later","error_code":35,"error_extra":{"event_id":"07c3fb965eaa4ec6a42e977c3e035c6b","retry_after":66},"error_tag":"LIMITS_REACHED","http_code":429}'
            """
            try:
                data = exception.response.json()
                retry_after = data.get("error_extra", {}).get("retry_after", 10)
                return float(retry_after) + 10
            except (json.JSONDecodeError, KeyError, ValueError, AttributeError):
                return 10.0

        def should_give_up(exception: Exception) -> bool:
            if isinstance(exception, httpx.HTTPStatusError):
                # Retry only 429 (rate limits) and 5xx (server errors)
                return (
                    exception.response.status_code != 429
                    and exception.response.status_code < 500
                )
            return False

        patched_status = backoff.on_exception(
            backoff.runtime,
            httpx.HTTPStatusError,
            giveup=should_give_up,
            value=extract_retry_time,
            max_tries=8,
        )(original_function)

        patched_network = backoff.on_exception(
            backoff.expo,
            httpx.RequestError,
            max_tries=30,
        )(patched_status)

        setattr(
            http_requests,
            target,
            patched_network,
        )

    patch_todoist_api.complete = True  # type: ignore[attr-defined]


patch_todoist_api()
