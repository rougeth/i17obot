import random
from urllib.parse import urljoin

import aiohttp
from decouple import config


TRANSIFEX_TOKEN = config("TRANSIFEX_TOKEN")
TRANSIFEX_API = "https://www.transifex.com/api/2/project/python-newest/"


async def transifex_api(url):
    auth = aiohttp.BasicAuth(login="api", password=TRANSIFEX_TOKEN)
    async with aiohttp.ClientSession(auth=auth) as session:
        url = urljoin(TRANSIFEX_API, url)
        async with session.get(url) as response:
            return await response.json()


async def random_string():
    strings = await transifex_api("resource/about/translation/pt_BR/strings/")
    strings = filter(lambda s: not s["reviewed"], strings)
    return random.choice(list(strings))
