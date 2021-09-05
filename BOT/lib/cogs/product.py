"""
    File: /lib/cogs/product.py
    Info: This cog handles all commands related to products
"""
import nextcord
from nextcord import message
from nextcord.ext.commands import Cog, command
from nextcord import Embed, Colour, colour, ui, Interaction, SelectOption, ButtonStyle
from datetime import datetime

from nextcord.ui.select import select
from nextcord.user import BU
from ..utils.api import *
from ..utils.database import find

productoptions = []

# Are you sure?
class AreYouSureView(ui.View):
    def __init__(self, context, Action, arg1):
        super().__init__(timeout=None)
        self.Action = Action
        self.arg1 = arg1
        self.context = context

    @ui.button(
        label="Yes", custom_id="products:yes_I_am_sure", style=ButtonStyle.success
    )
    async def iamsure(self, _, interaction: Interaction):
        if self.Action == "deleteproduct":
            deleteproduct(self.arg1)
            await interaction.message.delete()
            await interaction.channel.send(
                f"Deleted {self.arg1}.",
                delete_after=5.0,
                reference=self.context.message,
            )

    @ui.button(
        label="No", custom_id="products:no_I_am_not_sure", style=ButtonStyle.danger
    )
    async def noiamnotsure(self, _, interaction: Interaction):
        await interaction.message.delete()
        await interaction.channel.send(
            "Canceled action.", delete_after=5.0, reference=self.context.message
        )


# Delete view
class DeleteView(ui.View):
    def __init__(self, context):
        super().__init__(timeout=None)
        self.context = context
        global productoptions
        for product in getproducts():
            productoptions.append(
                SelectOption(label=product["name"], description=product["price"])
            )

    @ui.select(
        custom_id="products:delete_select",
        options=productoptions,  # SelectOption(label="Test", description="Test Option")
    )
    async def nextcord_help(self, _, interaction: Interaction):
        product = str(interaction.data["values"])[2:-2]
        await interaction.message.delete()
        await interaction.channel.send(
            f"Are you sure you would like to delete {product}?",
            view=AreYouSureView(self.context, "deleteproduct", product),
            reference=self.context.message,
        )


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
                    + str(product["description"])
                    + "\nProduct Price: "
                    + str(product["price"]),
                    False,
                )
            )

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text="Redon Tech RPH • By: parker02311")

        await ctx.send(embed=embed, reference=ctx.message)

    @command(
        name="createproduct",
        aliases=["newproduct", "makeproduct"],
        description="Create a new product.",
    )
    async def createproduct(self, ctx):
        questions = [
            "What do you want to call this product?",
            "What do you want the description of the product to be?",
            "What do you want the product price to be?",
        ]
        embedmessages = []
        usermessages = []
        awnsers = []

        def check(m):
            return m.content and m.author == ctx.author

        def emojicheck(self, user):
            return user == ctx.author

        for i, question in enumerate(questions):
            embed = Embed(
                title=f"Create Product (Question {i+1})",
                description=question,
                colour=ctx.author.colour,
                timestamp=datetime.utcnow(),
            )
            embed.set_footer(
                text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
            )
            embedmessage = await ctx.send(embed=embed)
            embedmessages.append(embedmessage)
            try:
                message = await self.bot.wait_for("message", timeout=200.0, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time")
                return
            if message.content.lower() == "cancel":
                usermessages.append(message)
                for message in embedmessages:
                    await message.delete()

                for message in usermessages:
                    await message.delete()

                await ctx.message.delete()
                await ctx.send("Canceled", delete_after=5.0)

                break
            else:
                usermessages.append(message)
                awnsers.append(message.content)

        lastbeforefinal = await ctx.send(
            "Creating final message this may take a moment."
        )

        for message in embedmessages:
            await message.delete()

        for message in usermessages:
            await message.delete()

        embed = Embed(
            title="Confirm Product Creation",
            description="✅ to confirm\n❌ to cancel",
            colour=ctx.author.colour,
            timestamp=datetime.utcnow(),
        )

        fields = [
            ("Name", awnsers[0], False),
            ("Description", awnsers[1], False),
            ("Price", awnsers[2], False),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text="Redon Tech RPH • By: parker02311")
        finalmessage = await ctx.send(embed=embed)
        await finalmessage.add_reaction("✅")
        await finalmessage.add_reaction("❌")
        await lastbeforefinal.delete()

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=200.0, check=emojicheck
            )
        except TimeoutError:
            await ctx.author.send("You didn't respond in time.")
            return

        if str(reaction.emoji) == "✅":
            try:
                createproduct(awnsers[0], awnsers[1], awnsers[2])
            except:
                await ctx.send(
                    "I was unable to create the product...", delete_after=5.0
                )
                raise

            embed = Embed(
                title="Product Created",
                description="The product was successfully created.",
                colour=ctx.author.colour,
                timestamp=datetime.utcnow(),
            )

            fields = [
                ("Name", awnsers[0], False),
                ("Description", awnsers[1], False),
                ("Price", awnsers[2], False),
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            embed.set_footer(text="Redon Tech RPH • By: parker02311")
            await ctx.send(embed=embed)
            await finalmessage.delete()
            await ctx.message.delete()

    @command(
        name="deleteproduct",
        aliases=["removeproduct", "terminateproduct", "fuckoffpieceofshitproduct"],
        description="Delete's a product.",
    )
    async def deleteproduct(self, ctx):
        await ctx.send(
            "Chose a product to delete", view=DeleteView(ctx), reference=ctx.message
        )
        """def emojicheck(self, user):
            return user == ctx.author

        try:
            product = find("products", {"name": name})
        except:
            await ctx.send(
                "I was unable to find any product matching that name.",
                delete_after=5.0,
                reference=ctx.message,
            )

        if product:
            embed = Embed(
                title="Delete Product",
                description=f"Are you sure you would like to delete {name}?\n✅ to delete\n❌ to cancel.",
                colour=ctx.author.colour,
                timestamp=datetime.utcnow(),
            )

            embedmessage = await ctx.send(embed=embed, reference=ctx.message)
            await embedmessage.add_reaction("✅")
            await embedmessage.add_reaction("❌")

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=200.0, check=emojicheck
                )
            except TimeoutError:
                await ctx.author.send(
                    "You didn't respond in time.",
                    delete_after=5.0,
                    reference=ctx.message,
                )
                return

            if str(reaction.emoji) == "✅":
                await embedmessage.delete()
                try:
                    deleteproduct(name)
                    await ctx.send(
                        "I deleted the product", delete_after=5.0, reference=ctx.message
                    )
                    await ctx.message.delete()
                except:
                    await ctx.send(
                        "I was unable to delete the product.",
                        delete_after=5.0,
                        reference=ctx.message,
                    )
                    raise
            else:
                await embedmessage.delete()
                await ctx.send("Canceled", delete_after=5.0, reference=ctx.message)
                await ctx.message.delete()"""

    @command(
        name="updateproduct",
        aliases=["changeproduct"],
        description="Update's a product.",
    )
    async def updateproduct(self, ctx, *, name):
        if name:
            pass
        else:
            ctx.send("A product name is required.", reference=ctx.message)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("product")
            await self.bot.stdout.send("`/lib/cogs/product.py` ready")
            print(" /lib/cogs/product.py ready")


def setup(bot):
    bot.add_cog(Product(bot))
