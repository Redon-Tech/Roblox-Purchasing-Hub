"""
    File: /lib/cogs/api.py
    Info: This cog runs the API alongside some bot stuff so thats pretty cool.
"""
from discord.ext.commands import Cog
from discord import Embed, Colour
from quart import Quart
from ..utils.database import db

app = Quart(__name__)


@app.route("/")
async def index():
    return {"message": "Ok"}


@app.route("/db/online")
async def db_online():
    """
    Used to check if the database is online
    """
    result = db.command("serverStatus")
    if result:
        return {"message": "Online"}
    else:
        return {"message": "Offline"}


class Api(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("api")
            await self.bot.stdout.send("`/lib/cogs/api.py` ready")
            print(" /lib/cogs/api.py ready")


def setup(bot):
    bot.loop.create_task(app.run_task("0.0.0.0"))
    bot.add_cog(Api(bot))
