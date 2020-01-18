import pytest

from i17obot.utils import docsurl


@pytest.mark.parametrize(
    "resource, url",
    (
        ("howto--logging-cookbook", "howto/logging-cookbook.html"),
        ("library--__future__", "library/__future__.html"),
        ("library--async-api-index", "library/async-api-index.html"),
        ("library--asyncio-protocol", "library/asyncio-protocol.html"),
        ("library--concurrent.futures", "library/concurrent.futures.html"),
        ("library--email_compat32-message", "library/email.compat32-message.html"),
        ("library--http_server", "library/http.server.html"),
        (
            "library--multiprocessing_shared_memory",
            "library/multiprocessing.shared_memory.html",
        ),
    ),
)
def test_docsurl(resource, url):
    assert docsurl(resource).endswith(url)
