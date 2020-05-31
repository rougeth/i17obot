import asyncio
import json
import sys

import click

import i17obot
from i17obot.reminder import reminder_all_users
from i17obot.transifex import download_all_strings


@click.group()
def main():
    pass


@main.command()
def run():
    click.echo("Running i17obot")
    i17obot.run()


@main.command()
@click.option("-u", "--user", type=int, multiple=True)
def reminder(user):
    click.echo("Running i17obot")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reminder_all_users(users=user))


def _main():
    file_to_save = sys.argv[1]
    strings = asyncio.run(download_all_strings())

    with open(file_to_save, mode="w") as fp:
        json.dump(strings, fp)


if __name__ == "__main__":
    main()
