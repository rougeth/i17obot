import random
from urllib.parse import quote, urljoin

import aiohttp
from async_lru import alru_cache
from decouple import config

TRANSIFEX_TOKEN = config("TRANSIFEX_TOKEN")
TRANSIFEX_API = "https://www.transifex.com/api/2/project/python-newest/"


@alru_cache()
async def transifex_api(url):
    auth = aiohttp.BasicAuth(login="api", password=TRANSIFEX_TOKEN)
    async with aiohttp.ClientSession(auth=auth) as session:
        url = urljoin(TRANSIFEX_API, url)
        async with session.get(url) as response:
            return await response.json()


async def random_resource():
    resources = await transifex_api(f"resources/")
    resources = [resource["slug"] for resource in resources]
    resources = filter(
        lambda r: r.split("--")[0] in ["bugs", "howto", "library"], resources
    )
    return random.choice(list(resources))


async def random_string(resource=None, translated=None, reviewed=None, max_size=None):
    if not resource:
        resource = await random_resource()

    strings = await transifex_api(
        f"resource/{resource}/translation/pt_BR/strings/?details"
    )

    if translated is not None:
        strings = filter(lambda s: bool(s["translation"]) == translated, strings)

    if reviewed is not None:
        strings = filter(lambda s: s["reviewed"] == reviewed, strings)

    if max_size is not None:
        strings = filter(lambda s: len(s["source_string"]) <= max_size, strings)

    strings = list(strings)
    if not strings:
        if max_size:
            max_size += 300

        return await random_string(
            translated=translated, reviewed=reviewed, max_size=max_size
        )

    return resource, random.choice(list(strings))


def transifex_string_url(resource, key):
    query_string = f"text:'{key[:20]}'"
    return (
        "https://www.transifex.com/"
        f"python-doc/python-newest/translate/#pt_BR/{resource}/1"
        f"?q={quote(query_string)}"
    )
