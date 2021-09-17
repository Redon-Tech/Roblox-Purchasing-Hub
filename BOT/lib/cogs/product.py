"""
    File: /lib/cogs/product.py
    Info: This cog handles all commands related to products
"""
import nextcord
from nextcord import message
from nextcord.components import Button
from nextcord.ext.commands import Cog, command
from nextcord import Embed, Colour, colour, ui, Interaction, SelectOption, ButtonStyle
from datetime import datetime
from nextcord.ui.button import button
from nextcord.ui.select import select
from nextcord.user import BU
from ..utils.api import *  # Imports everything from the API util
from ..utils.database import find
import json

productoptions = []

# Cancel Button
class CancelView(ui.View):
    def __init__(self, context):
        super().__init__(timeout=None)
        self.context = context
        self.canceled = False

    @ui.button(label="Cancel", style=ButtonStyle.danger, custom_id="products:cancel")
    async def cancel(self, _, interaction: Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Canceled", ephemeral=True)
        self.canceled = True
        self.stop()


# Are you sure?
class AreYouSureView(ui.View):
    def __init__(self, context, Action, *args):
        super().__init__(timeout=None)
        self.Action = Action
        self.args = args
        self.context = context

    @ui.button(
        label="Yes", custom_id="products:yes_I_am_sure", style=ButtonStyle.success
    )
    async def iamsure(self, _, interaction: Interaction):
        if self.Action == "deleteproduct":
            try:
                deleteproduct(self.args[0])
                await interaction.message.delete()
                await interaction.response.send_message(
                    f"Deleted {self.args[0]}.",
                    ephemeral=True,
                )
                self.stop()
            except:
                await interaction.message.delete()
                await interaction.response.send_message(
                    f"Failed to delete {self.args[0]}.",
                    ephemeral=True,
                )
                self.stop()
        if self.Action == "updateproduct":
            try:
                updateproduct(self.args[0], self.args[1], self.args[2], self.args[3])
                await interaction.message.delete()
                await interaction.response.send_message(
                    f"Updated {self.args[0]}.",
                    ephemeral=True,
                )
                self.stop()
            except:
                await interaction.message.delete()
                await interaction.response.send_message(
                    f"Failed to update {self.args[0]}.",
                    ephemeral=True,
                )
                self.stop()

    @ui.button(
        label="No", custom_id="products:no_I_am_not_sure", style=ButtonStyle.danger
    )
    async def noiamnotsure(self, _, interaction: Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Canceled action.", ephemeral=True)
        self.stop()


# Delete view
class DeleteView(ui.View):
    def __init__(self, context):
        super().__init__(timeout=None)
        self.context = context
        global productoptions
        productoptions.clear()
        for product in getproducts():
            productoptions.append(
                SelectOption(label=product["name"], description=product["price"])
            )

    @ui.select(
        custom_id="products:delete_select",
        options=productoptions,
    )
    async def delete_select(self, _, interaction: Interaction):

        product = str(interaction.data["values"])[2:-2]
        await interaction.message.delete()
        await interaction.channel.send(
            f"Are you sure you would like to delete {product}?",
            view=AreYouSureView(self.context, "deleteproduct", product),
            reference=self.context.message,
        )


# Update View's

## What to update
class WhatUpdateView(ui.View):
    def __init__(self, context, product, bot):
        super().__init__(timeout=600.0)
        self.context = context
        self.product = getproduct(product)
        self.bot = bot

    @ui.button(
        label="Name", style=ButtonStyle.primary, custom_id="products:update_name"
    )
    async def update_name(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.product['name']}",
            description=f"What would you like to change the name to?",
            colour=Colour.blue(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(
            text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
        )
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.context.author

        try:
            message = await self.bot.wait_for("message", timeout=600.0, check=check)
        except TimeoutError:
            await interaction.message.delete()
            await interaction.response.send_message("Timed Out", ephemeral=True)
            self.stop()

        if not message == None and view.canceled == False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await interaction.response.send_message("Canceled", ephemeral=True)
                self.stop()
            else:
                await interaction.message.delete()
                await self.context.send(
                    f"Are you sure you would like to change {self.product['name']} to {message.content}?",
                    view=AreYouSureView(
                        self.context,
                        "updateproduct",
                        self.product["name"],
                        message.content,
                        self.product["description"],
                        self.product["price"],
                    ),
                    reference=self.context.message,
                )

    @ui.button(
        label="Description",
        style=ButtonStyle.primary,
        custom_id="products:update_description",
    )
    async def update_description(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.product['name']}",
            description=f"What would you like to change the description to?",
            colour=Colour.blue(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(
            text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
        )
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.context.author

        try:
            message = await self.bot.wait_for("message", timeout=600.0, check=check)
        except TimeoutError:
            await interaction.message.delete()
            await interaction.response.send_message("Timed Out", ephemeral=True)
            self.stop()

        if not message == None and view.canceled == False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await interaction.response.send_message("Canceled", ephemeral=True)
                self.stop()
            else:
                await interaction.message.delete()
                await self.context.send(
                    f"Are you sure you would like to change {self.product['description']} to {message.content}?",
                    view=AreYouSureView(
                        self.context,
                        "updateproduct",
                        self.product["name"],
                        self.product["name"],
                        message.content,
                        self.product["price"],
                    ),
                    reference=self.context.message,
                )

    @ui.button(
        label="Price", style=ButtonStyle.primary, custom_id="products:update_price"
    )
    async def update_price(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.product['name']}",
            description=f"What would you like to change the description to?",
            colour=Colour.blue(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(
            text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
        )
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.context.author

        try:
            message = await self.bot.wait_for("message", timeout=600.0, check=check)
        except TimeoutError:
            await interaction.message.delete()
            await interaction.response.send_message("Timed Out", ephemeral=True)
            self.stop()

        if not message == None and view.canceled == False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await interaction.response.send_message("Canceled", ephemeral=True)
                self.stop()
            else:
                await interaction.message.delete()
                await self.context.send(
                    f"Are you sure you would like to change {self.product['price']} to {int(message.content)}?",
                    view=AreYouSureView(
                        self.context,
                        "updateproduct",
                        self.product["name"],
                        self.product["name"],
                        self.product["description"],
                        int(message.content),
                    ),
                    reference=self.context.message,
                )

    @ui.button(
        label="cancel", style=ButtonStyle.danger, custom_id="products:update_cancel"
    )
    async def update_cancel(self, _, interaction: Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Canceled", ephemeral=True)
        self.stop()


## Initial View
class InitialUpdateView(ui.View):
    def __init__(self, context, bot):
        super().__init__(timeout=600.0)
        self.context = context
        self.bot = bot
        global productoptions
        productoptions.clear()
        for product in getproducts():
            productoptions.append(
                SelectOption(label=product["name"], description=product["price"])
            )

    @ui.select(
        custom_id="products:update_select",
        options=productoptions,
    )
    async def update_select(self, _, interaction: Interaction):
        product = str(interaction.data["values"])[2:-2]
        embed = Embed(
            title=f"Update {product}",
            description=f"What would you like to change?",
            colour=Colour.blue(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text="Redon Tech RPH • By: parker02311")
        await interaction.message.edit(
            "", embed=embed, view=WhatUpdateView(self.context, product, self.bot)
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

    @command(
        name="updateproduct",
        aliases=["changeproduct"],
        description="Update's a product.",
    )
    async def updateproduct(self, ctx):
        await ctx.send(
            "Chose a product to update.",
            view=InitialUpdateView(ctx, self.bot),
            reference=ctx.message,
        )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("product")
            await self.bot.stdout.send("`/lib/cogs/product.py` ready")
            print(" /lib/cogs/product.py ready")


def setup(bot):
    bot.add_cog(Product(bot))
