"""
    File: /lib/cogs/product.py
    Info: This cog handles all commands related to products
"""
from discord.ext.commands import Cog, command
from discord import Embed, Colour, colour
from datetime import datetime
from ..utils.api import *


class Product(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="products",
        aliases=["listproducts", "viewproducts", "allproducts"],
        description="Sends a list of all products.",
    )
    async def getproducts(self, ctx):
        dbresponse = getproducts()
        embed = Embed(
            title="Products",
            description=f"Here is all the products I was able to get for this server!",
            colour=ctx.author.colour,
            timestamp=datetime.utcnow(),
        )

        fields = []

        for product in dbresponse:
            fields.append(
                (
                    product["name"],
                    "Product Description: "
                    + product["description"]
                    + "\nProduct Price: "
                    + product["price"],
                    False,
                )
            )

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed, reference=ctx.message)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("product")
            await self.bot.stdout.send("`/lib/cogs/product.py` ready")
            print(" /lib/cogs/product.py ready")


def setup(bot):
    bot.add_cog(Product(bot))
