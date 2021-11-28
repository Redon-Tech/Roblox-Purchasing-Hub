"""
    File: /lib/bot/__init__.py
    Usage: Used to create the bot and launch cogs
    Info: Bot is imported as BotBase so I can make a class called Bot. Theres not much to this file.
"""

from asyncio import sleep
from glob import glob
from nextcord.ext.commands import Bot as BotBase
from nextcord.ext.commands import (
    CommandNotFound,
    Context,
    BadArgument,
    MissingRequiredArgument,
    CommandOnCooldown,
)
from nextcord.errors import HTTPException, Forbidden
from nextcord import Intents, DMChannel
from ..utils.util import UserNotVerified
import json
import os


COGS = [path.split(os.sep)[-1][:-3] for path in glob("./BOT/lib/cogs/*.py")]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        with open("./BOT/lib/bot/config.json") as config_file:
            self.config = json.load(config_file)

        self.PREFIX = self.config["prefix"]
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        super().__init__(
            command_prefix=self.PREFIX,
            owner_ids=self.config["ownerids"],
            intents=Intents.all(),
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" /lib/cogs/{cog}.py setup")

        print("  Cogs Setup")

    def run(self, version, istest):
        self.VERSION = version

        print("Running Cog Setup...")
        self.setup()
        self.istest = istest

        # with open("./BOT/lib/bot/token", "r", encoding="utf-8") as tf:
        #    self.TOKEN = tf.read()

        print("Running Bot...")
        super().run(self.config["token"], reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("Bot is still setting up please wait.")

    async def on_connect(self):
        print("Bot Connected")

    async def on_disconnect(self):
        print("Bot Disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong...")

        else:
            await self.stdout.send("An error has occured.")

        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif isinstance(exc, BadArgument):
            await ctx.send(
                f"You inputed an invalid argument, use {self.PREFIX}help to see all the required arguments.",
                reference=ctx.message,
            )

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(
                f"You left out a vital argument, use {self.PREFIX}help to see all the required arguments.",
                reference=ctx.message,
            )

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown for {exc.retry_after:,.2f} more seconds.",
                reference=ctx.message,
            )

        elif isinstance(exc, HTTPException):
            await ctx.send("I was unable to send the message.", reference=ctx.message)

        elif isinstance(exc, UserNotVerified):
            await ctx.send(
                "Only verified users can use this command.", reference=ctx.message
            )

        elif hasattr(exc, "original"):
            if isinstance(exc.original, Forbidden):
                await ctx.send(
                    "I do not have permission to do that.", reference=ctx.message
                )

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(self.config["guild"])
            self.stdout = self.get_channel(self.config["standardoutput"])
            await self.stdout.purge(limit=1000)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            await self.stdout.send("Bot Ready")
            print("  Bot Ready")

            # meta = self.get_cog("Meta")
            # await meta.set()

            if self.istest:
                await self.stdout.send("This was a test deploy.")
                await bot.close()

        else:
            print("Bot Reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            if not isinstance(message.channel, DMChannel):
                await self.process_commands(message)


bot = Bot()
