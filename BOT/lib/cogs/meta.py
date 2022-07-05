"""
    File: /lib/cogs/meta.py
    Info: More miscallaneous functions of the bot, like status setting, ping command, etc.
"""
from nextcord.ext.commands import Cog, command
from nextcord import Embed, Colour, Activity, ActivityType
from datetime import datetime
from time import time


class Meta(Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def message(self):
        return self._message.format(
            users=len(self.bot.users),
            prefix=self.bot.config["prefix"],
            version=self.bot.VERSION,
        )

    @message.setter
    def message(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            raise ValueError("Invalid activity type")

        self._message = value

    def status(self, value):
        if value not in (
            "online",
            "idle",
            "dnd",
            "offline",
            "invisible",
            "do_not_disturb",
        ):
            raise ValueError("Invalid status")

        self._status = value

    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)
        _status = self.status
        await self.bot.change_presence(
            activity=Activity(
                status=_status,
                name=_name,
                type=getattr(ActivityType, _type, ActivityType.playing),
            )
        )

    @command()
    async def ping(self, ctx):
        start = time()
        message = await ctx.send(
            f"Pong :ping_pong:! **{self.bot.latency*100:,.0f} ms**"
        )
        end = time()

        await message.edit(
            content=f"Pong :ping_pong:! **Latency: {self.bot.latency*100:,.0f} ms** | **Response Time {(end-start)*1000:,.0f} ms**"
        )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("meta")
            await self.bot.stdout.send("`/lib/cogs/meta.py` ready")
            print(" /lib/cogs/meta.py ready")


def setup(bot):
    bot.add_cog(Meta(bot))
