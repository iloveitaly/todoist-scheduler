"""
This was an experiment that didn't work. It's hard to determine if a URL is broken outside of DNS records
not existing. It also just didn't seem to be that many urls after I ran this across >2k tasks.
"""

import datetime
import re
from urllib.parse import urlparse

import dns.resolver
import funcy_pipe as fp
import regex
import requests
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

from todoist_scheduler.internet import wait_for_internet_connection

from .utils import log

# https://urlregex.com
URL_REGEX = (
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

DNS_ONLY_CHECK = False
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.1"


def url_has_no_ip(url):
    domain = urlparse(url).hostname
    return domain_has_no_ip(domain)


def domain_has_no_ip(domain, dns_server="8.8.8.8"):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]

    try:
        resolver.resolve(domain, "A")
        return False  # IP record found
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.Timeout,
        dns.resolver.NoNameservers,
    ):
        return True  # No IP record found


def is_url_dead(url: str):
    # not a real URL
    if not url.startswith(("http://", "https://")):
        return False

    # linkedin won't let us check :/
    if url.startswith(
        (
            "https://www.linkedin.com/",
            "https://docs.google.com",
            "https://google.com",
            "https://x.com",
            "https://twitter.com",
        )
    ):
        return False

    # first, let's check DNS
    if url_has_no_ip(url):
        log.warn("no IP found for domain", url=url)
        return True

    if DNS_ONLY_CHECK:
        return False

    proxy_url = ""
    proxies = {}

    if proxy_url:
        proxies = {
            "http": f"http://{proxy_url}",
            "https": f"http://{proxy_url}",
        }

    try:
        # {'User-Agent': 'python-requests/2.32.3', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
        response = requests.get(
            url,
            allow_redirects=True,
            headers={
                # many sites need a valid agent
                # https://www.useragents.me
                "User-Agent": USER_AGENT
            },
            proxies=proxies,
        )

        if response.status_code != 200 and response.status_code != 404:
            log.info("strange status code", url=url, status_code=response.status_code)

        fully_dead = response.status_code == 404

        if fully_dead:
            log.info("dead link", url=url)
            return True

        return False
    except requests.RequestException as e:
        log.warn("error checking URL", url=url, error=e)
        return False


def is_old_task(task: Task) -> bool:
    old_in_days = 180
    created_at = datetime.datetime.fromisoformat(task.created_at.replace("Z", "+00:00"))
    return (datetime.datetime.now(datetime.UTC) - created_at).days >= old_in_days


def only_fully_dead_urls(task_tuple: tuple[list[str], Task]) -> Task | None:
    url_list, task = task_tuple

    # no urls
    if not url_list:
        return None

    dead_urls, alive_urls = url_list | fp.lsplit(is_url_dead)

    if not alive_urls:
        return task

    if list(dead_urls):
        # there are some dead, but not all
        log.info("partially dead links", dead=dead_urls, alive=alive_urls)
        return None

    # then all are dead
    return None


def extract_urls_from_task(task: Task) -> tuple[list[str], Task]:
    urls = extract_urls_from_markdown_string(task.content)
    return urls, task


def extract_urls_from_markdown_string(content: str) -> list[str]:
    """
    Simple regex does't work to extract URLs, and there isn't a markdoc AST like javascript

    https://stackoverflow.com/questions/67940820/how-to-extract-markdown-links-with-a-regex

    Note that only title is used, not description. This is tied to my todo list structure.
    """

    pattern = regex.compile(r"\[([^][]+)\](\(((?:[^()]+|(?2))+)\))")
    links = []

    for match in pattern.finditer(content):
        description, _, url = match.groups()
        links.append(url.strip())

    if not links:
        # there may be bare links depending on how the content was entered
        links = re.findall(URL_REGEX, content)

    return links


def remove_dead_link_tasks(dry_run, api_key):
    wait_for_internet_connection()

    api = TodoistAPI(api_key)
    tasks = api.get_tasks()

    log.info("inspecting tasks", total=len(tasks))

    def close_task(task):
        if dry_run:
            log.info("would close task", task=task)
            return

        log.info("closing task", task=task)
        api.close_task(task.id)

    tasks | fp.filter(is_old_task) | fp.map(extract_urls_from_task) | fp.map(
        only_fully_dead_urls
    ) | fp.compact() | fp.map(close_task) | fp.to_list()
