"""
    File: /lib/cogs/product.py
    Info: This cog handles all commands related to products
"""
from discord.ext.commands import Cog, command
from discord import Embed, Colour, colour


class Product(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="products",
        aliases=["listproducts", "viewproducts", "allproducts"],
        description="Sends a list of all products.",
    )
    async def getproducts(self, ctx):
        pass

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("product")
            await self.bot.stdout.send("`/lib/cogs/product.py` ready")
            print(" /lib/cogs/product.py ready")


def setup(bot):
    bot.add_cog(Product(bot))
