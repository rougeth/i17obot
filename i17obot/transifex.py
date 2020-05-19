import asyncio
import itertools
import logging
import random
from urllib.parse import quote, urljoin

import aiohttp
from async_lru import alru_cache
from decouple import config

TRANSIFEX_TOKEN = config("TRANSIFEX_TOKEN")

TRANSIFEX_API = {
    "python": "https://www.transifex.com/api/2/project/python-newest/",
    "jupyter": "https://www.transifex.com/api/2/project/jupyter-meta-documentation/",
}

PROJECT_URL = {
    "python": (
        "https://www.transifex.com/"
        "python-doc/python-newest/translate/#{language}/{resource}/1"
        "?q={query_string}"
    ),
    "jupyter": (
        "https://www.transifex.com/"
        "project-jupyter/jupyter-meta-documentation/translate/#{language}/{resource}/1"
        "?q={query_string}"
    ),
}

FILTER_RESOURCES_TO_BE_TRANSLATED = {
    "python": lambda r: r.split("--")[0] in ["bugs", "howto", "library"],
    "jupyter": None,
}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


async def transifex_api(url, project, data=None, retrying=False):
    if retrying:
        logger.info("retrying url=%s", url)

    auth = aiohttp.BasicAuth(login="api", password=TRANSIFEX_TOKEN)
    async with aiohttp.ClientSession(auth=auth) as session:
        http_method = session.put if data else session.get
        args = {"json": data} if data else {}

        try:
            async with http_method(
                urljoin(TRANSIFEX_API[project], url), **args
            ) as response:
                logger.info("url=%s, status_code=%s", url, response.status)
                return await response.json()

        except aiohttp.client_exceptions.ClientConnectorSSLError as e:
            logger.error("url=%s, error=%s", url, e)
            if not retrying:
                await asyncio.sleep(2)
                return await transifex_api(url, project, retrying=True)
            raise


async def random_resource(project):
    resources = await transifex_api(f"resources/", project)
    resources = [resource["slug"] for resource in resources]

    if FILTER_RESOURCES_TO_BE_TRANSLATED[project]:
        resources = filter(FILTER_RESOURCES_TO_BE_TRANSLATED[project], resources)

    resource = random.choice(list(resources))
    logger.info("random_resource, resource=%s", resource)
    return resource


async def strings_from_resource(resource, language, project):
    strings = await transifex_api(
        f"resource/{resource}/translation/{language}/strings/?details", project,
    )
    logger.info(
        "getting strings from resource, resource=%s, strings_found=%s",
        resource,
        len(strings),
    )
    for string in strings:
        string["resource"] = resource

    return strings


async def random_string(
    language, project, resource=None, translated=None, reviewed=None, max_size=None
):
    if not resource:
        resource = await random_resource(project)

    strings = await strings_from_resource(resource, language, project)

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

        resource = None
        return await random_string(
            language, project, resource, translated, reviewed, max_size
        )

    return resource, random.choice(list(strings))


def transifex_string_url(resource, key, language, project):
    return PROJECT_URL[project].format(
        resource=resource, language=language, query_string=quote(f"text:'{key[:20]}'"),
    )


async def translate_string(resource, string_hash, translation):
    await transifex_api(
        f"resource/{resource}/translation/pt_BR/string/{string_hash}/",
        data={"translation": translation},
    )


async def download_all_strings(language):
    """ Download all strings in Transifex to JSON file
    """
    resources = await transifex_api(f"resources/", "python")
    resources = [resource["slug"] for resource in resources]
    print("Resources", len(resources))

    sema = asyncio.Semaphore(10)
    async with sema:
        strings = await asyncio.gather(
            *[strings_from_resource(resource, language) for resource in resources]
        )
    strings = list(itertools.chain.from_iterable(strings))
    print("Strings", len(resources))
    return strings
