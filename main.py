"""
Main file to start up bot
"""

__version__ = "0.0.1"
__licence__ = "MIT License"
__authors__ = ["micfun123", "fusionsid"]

import os
import time
import json

import discord
from discord.ext import commands

from dotenv import load_dotenv

from rich.progress import Progress
from rich.console import Console
from rich.traceback import install

install()


class Config:
    """
    A config class for the bot

    Attributes
    ----------
        prefix: str
        suggestion_channel:
        weekly_challenges_channel:
    """

    def __init__(self):
        with open("config.json") as f:
            data = json.load(f)

        self.prefix = data["prefix"] if data["prefix"] is not None else "#"
        self.suggestion_channel = data["suggestion_channels"]
        self.weekly_challenges_channel_post = data["weekly_challenge_post"]
        self.weekly_challenges_channel_get = data["weekly_challenge_get"]


class CodeCave(commands.Bot):
    """
    The CodeCave Class (subclass of: `discord.ext.commands.Bot`)
    """

    def __init__(self):

        self.cogs_list = []
        self.config = Config()
        self.version = __version__
        self.console = Console()

        intents = discord.Intents.all()
        allowed_mentions = discord.AllowedMentions(everyone=False)

        super().__init__(
            intents=intents,
            help_command=None,
            case_insensitive=True,
            command_prefix=self.config.prefix,
            allowed_mentions=allowed_mentions,
        )


def start_bot(client):
    cogs = []

    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            cogs.append(f"cogs.{filename[:-3]}")

    print("\n")
    client.cogs_list = cogs

    with Progress() as progress:
        loading_cogs = progress.add_task("[bold green]Loading Cogs", total=len(cogs))
        while not progress.finished:
            for cog in cogs:
                client.load_extension(cog)
                time.sleep(0.1)
                progress.update(
                    loading_cogs,
                    advance=1,
                    description=f"[bold green]Loaded[/] [blue]{cog}[/]",
                )
        progress.update(loading_cogs, description="[bold green]Loaded all cogs")

    time.sleep(1)
    client.run(os.environ["TOKEN"])


if __name__ == "__main__":
    load_dotenv()

    client = CodeCave()

    start_bot(client)
