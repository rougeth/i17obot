import asyncio
import itertools
import json
import sys

from transifex import strings_from_resource, transifex_api


async def download_all_strings(file_to_save):
    """ Download all strings in Transifex to JSON file
    """
    resources = await transifex_api(f"resources/")
    resources = [resource["slug"] for resource in resources]
    print("Resources", len(resources))

    sema = asyncio.Semaphore(10)
    async with sema:
        strings = await asyncio.gather(
            *[strings_from_resource(resource) for resource in resources]
        )
    strings = list(itertools.chain.from_iterable(strings))
    print("Strings", len(resources))

    with open(file_to_save, mode="w") as fp:
        json.dump(strings, fp)


if __name__ == "__main__":
    asyncio.run(download_all_strings(sys.argv[1]))
