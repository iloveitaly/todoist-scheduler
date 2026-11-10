from unittest.mock import patch

import httpx
import pytest
from todoist_api_python import api as todoist_api
from todoist_api_python._core import http_requests

from todoist_scheduler.patch import (
    extract_retry_time,
    patch_todoist_api,
    should_give_up,
    with_retry,
)


def _status_error(status_code: int, json_data: dict | None = None, text: str = ""):
    request = httpx.Request("GET", "https://api.todoist.com/api/v1/tasks")
    response = httpx.Response(
        status_code=status_code,
        json=json_data,
        text=text if json_data is None else None,
        request=request,
    )
    return httpx.HTTPStatusError("error", request=request, response=response)


def test_patch_applies_to_todoist_api():
    patch_todoist_api()
    for target in ["delete", "get", "post"]:
        patched_fn = getattr(http_requests, target)
        orig_fn = getattr(http_requests, f"original_{target}")
        assert patched_fn is not orig_fn
        assert getattr(todoist_api, target) is patched_fn


def test_extract_retry_time():
    err_429 = _status_error(429, json_data={"error_extra": {"retry_after": 66}})
    assert extract_retry_time(err_429) == 76.0

    err_502 = _status_error(502, text="Bad Gateway")
    assert extract_retry_time(err_502) == 10.0


def test_should_give_up():
    assert should_give_up(_status_error(429)) is False
    assert should_give_up(_status_error(502)) is False
    assert should_give_up(_status_error(503)) is False
    assert should_give_up(_status_error(404)) is True
    assert should_give_up(httpx.ConnectTimeout("timeout")) is False


def test_with_retry_503_and_404():
    calls = 0

    @with_retry
    def flaky():
        nonlocal calls
        calls += 1
        if calls < 2:
            raise _status_error(503)
        return "ok"

    with patch("time.sleep"):
        assert flaky() == "ok"
    assert calls == 2

    @with_retry
    def not_found():
        raise _status_error(404)

    with pytest.raises(httpx.HTTPStatusError):
        not_found()
