"""
    File: /lib/cogs/meta.py
    Info: More miscallaneous functions of the bot, like status setting, ping command, etc.
"""
from nextcord.ext.commands import Cog, is_owner
from nextcord import Embed, Colour, Activity, ActivityType
from datetime import datetime
from time import time
from ..utils.api import *
from ..utils.command import command


class Meta(Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def message(self):
        return self._message.format(
            users=len(self.bot.users),
            prefix=self.bot.config["discord"]["commands"]["prefix"],
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

    @Cog.listener()
    async def on_member_join(self, member):
        await self.set()

    @Cog.listener()
    async def on_raw_member_remove(self, member):
        await self.set()

    @command(name="ping", brief="Check the latency and response time of the bot.")
    async def ping(self, ctx):
        start = time()
        message = await ctx.send(
            f"Pong :ping_pong:! **{self.bot.latency*100:,.0f} ms**"
        )
        end = time()

        await message.edit(
            content=f"Pong :ping_pong:! **Latency: {self.bot.latency*100:,.0f} ms** | **Response Time {(end-start)*1000:,.0f} ms**"
        )

    @command(name="migrateuserpurchases", no_slash=True)
    @is_owner()
    async def migrate_user_purchases(self, ctx):
        message = await ctx.send(
            "Please wait migrating user purchases from name to ID, look in output for any errors with the migration."
        )
        for user in getusers():
            try:
                for product in user["purchases"]:
                    try:
                        revokeproduct(user["_id"], product)
                        giveproduct(user["_id"], product)
                    except Exception as e:
                        print(
                            f"Unable to transfer {user['_id']}'s {product} because of ",
                            e,
                        )
            except Exception as e:
                print(f"Unable to get {user['_id']}'s purchases because of ", e)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("meta")
            await self.bot.stdout.send("`/lib/cogs/meta.py` ready")
            print(" /lib/cogs/meta.py ready")


def setup(bot):
    bot.add_cog(Meta(bot))
