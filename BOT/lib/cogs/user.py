"""
    File: /lib/cogs/user.py
    Info: This cog handles all the commands for user facing commands
"""
from nextcord.ext.commands import Cog, command
from nextcord import Embed, Colour
from datetime import datetime


class User(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("user")
            await self.bot.stdout.send("`/lib/cogs/user.py` ready")
            print(" /lib/cogs/user.py ready")


def setup(bot):
    bot.add_cog(User(bot))
