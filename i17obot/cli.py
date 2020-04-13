import asyncio
import json
import sys

from transifex import download_all_strings


def main():
    file_to_save = sys.argv[1]
    strings = asyncio.run(download_all_strings())

    with open(file_to_save, mode="w") as fp:
        json.dump(strings, fp)


if __name__ == "__main__":
    main()
