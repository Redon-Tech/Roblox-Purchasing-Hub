"""
    File: /lib/cogs/product.py
    Info: This cog handles all commands related to products
"""
import nextcord
from nextcord import message
from nextcord.components import Button
from nextcord.errors import Forbidden
from nextcord.ext.commands import Cog, command, has_permissions
from nextcord import Embed, Colour, colour, ui, Interaction, SelectOption, ButtonStyle
from datetime import datetime
from nextcord.ui.button import button
from nextcord.ui.select import select
from nextcord.user import BU
from ..utils.api import *  # Imports everything from the API util
from ..utils.database import find
from ..utils.util import AreYouSureView
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
            timestamp=nextcord.utils.utcnow(),
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

        if not message is None and view.canceled is False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await interaction.response.send_message("Canceled", ephemeral=True)
                self.stop()
            else:
                await interaction.message.delete()
                view = AreYouSureView(self.context)
                message = await self.context.send(
                    f"Are you sure you would like to change {self.product['name']} to {message.content}?",
                    view=view,
                    reference=self.context.message,
                )
                await view.wait()

                if view.Return == None:
                    await message.delete()
                    await interaction.response.send_message("Timed out", ephemeral=True)
                elif view.Return == False:
                    await message.delete()
                    await interaction.response.send_message("Canceled update", ephemeral=True)
                elif view.Return == True:
                    try:
                        updateproduct(
                            self.product["name"], message.content, self.product["description"], self.product["price"], self.product["attachments"]
                        )
                        await interaction.message.delete()
                        name = self.product["name"]
                        await interaction.response.send_message(
                            f"Updated {name}.",
                            ephemeral=True,
                        )
                    except:
                        await interaction.message.delete()
                        await interaction.response.send_message(
                            f"Failed to update {self.args[0]}.",
                            ephemeral=True,
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
            timestamp=nextcord.utils.utcnow(),
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

        if not message is None and view.canceled is False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await interaction.response.send_message("Canceled", ephemeral=True)
                self.stop()
            else:
                await interaction.message.delete()
                view = AreYouSureView(self.context)
                await self.context.send(
                    f"Are you sure you would like to change {self.product['description']} to {message.content}?",
                    view=view,
                    reference=self.context.message,
                )
                await view.wait()

                if view.Return == None:
                    await message.delete()
                    await interaction.response.send_message("Timed out", ephemeral=True)
                elif view.Return == False:
                    await message.delete()
                    await interaction.response.send_message("Canceled update", ephemeral=True)
                elif view.Return == True:
                    try:
                        updateproduct(
                            self.product["name"], self.product["name"], message.content, self.product["price"], self.product["attachments"]
                        )
                        await interaction.message.delete()
                        name = self.product["name"]
                        await interaction.response.send_message(
                            f"Updated {name}.",
                            ephemeral=True,
                        )
                    except:
                        await interaction.message.delete()
                        await interaction.response.send_message(
                            f"Failed to update {self.args[0]}.",
                            ephemeral=True,
                        )

    @ui.button(
        label="Price", style=ButtonStyle.primary, custom_id="products:update_price"
    )
    async def update_price(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.product['name']}",
            description=f"What would you like to change the price to?",
            colour=Colour.blue(),
            timestamp=nextcord.utils.utcnow(),
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

        if not message is None and view.canceled is False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await interaction.response.send_message("Canceled", ephemeral=True)
                self.stop()
            else:
                await interaction.message.delete()
                view = AreYouSureView(self.context)
                await self.context.send(
                    f"Are you sure you would like to change {self.product['price']} to {int(message.content)}?",
                    view=view,
                    reference=self.context.message,
                )
                await view.wait()

                if view.Return == None:
                    await message.delete()
                    await interaction.response.send_message("Timed out", ephemeral=True)
                elif view.Return == False:
                    await message.delete()
                    await interaction.response.send_message("Canceled update", ephemeral=True)
                elif view.Return == True:
                    try:
                        updateproduct(
                            self.product["name"], self.product["name"], self.product["description"], int(message.content), self.product["attachments"]
                        )
                        await interaction.message.delete()
                        name = self.product["name"]
                        await interaction.response.send_message(
                            f"Updated {name}.",
                            ephemeral=True,
                        )
                    except:
                        await interaction.message.delete()
                        await interaction.response.send_message(
                            f"Failed to update {self.args[0]}.",
                            ephemeral=True,
                        )

    @ui.button(
        label="Attachments",
        style=ButtonStyle.primary,
        custom_id="products:update_attachments",
    )
    async def update_attachments(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.product['name']}",
            description=f'Please post the attachments now. Say "Done" when you are done.',
            colour=Colour.blue(),
            timestamp=nextcord.utils.utcnow(),
        )

        embed.set_footer(
            text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
        )

        fields = [
            (
                "Attachments",
                "None",
                False,
            )
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.author == self.context.author

        attachments = []

        while True:
            try:
                message = await self.bot.wait_for("message", timeout=600.0, check=check)
            except TimeoutError:
                await interaction.message.delete()
                await interaction.response.send_message("Timed Out", ephemeral=True)
                self.stop()

            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await self.context.send(
                    "Canceled", reference=self.context.message, delete_after=5.0
                )

                break
            if message.content.lower() == "done":
                break
            elif not message.attachments == [] and message.attachments:
                for attachment in message.attachments:
                    attachments.append(attachment.url)
                    embed = Embed(
                        title=f"Update {self.product['name']}",
                        description=f'Please post the attachments now. Say "Done" when you are done.',
                        colour=Colour.blue(),
                        timestamp=nextcord.utils.utcnow(),
                    )

                    embed.set_footer(
                        text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
                    )

                    fields = [
                        (
                            "Attachments",
                            "\n".join([attachment for attachment in attachments]),
                            False,
                        )
                    ]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    embed.set_footer(text="Pembroke Bot • By: parker02311")
                    await interaction.message.edit("", embed=embed, view=None)
                    await self.context.send(
                        "It is recommended to not delete this message unless needed.",
                        reference=message,
                    )

        if attachments:
            await interaction.message.delete()
            view = AreYouSureView(self.context)
            await self.context.send(
                f"Are you sure you would like to change {self.product['attachments']} to {attachments}?",
                view=view,
                reference=self.context.message,
            )
            await view.wait()

            if view.Return == None:
                await message.delete()
                await interaction.response.send_message("Timed out", ephemeral=True)
            elif view.Return == False:
                await message.delete()
                await interaction.response.send_message("Canceled update", ephemeral=True)
            elif view.Return == True:
                try:
                    updateproduct(
                        self.product["name"], self.product["name"], self.product["description"], self.product["price"], attachments
                    )
                    await interaction.message.delete()
                    name = self.product["name"]
                    await interaction.response.send_message(
                        f"Updated {name}.",
                        ephemeral=True,
                    )
                except:
                    await interaction.message.delete()
                    await interaction.response.send_message(
                        f"Failed to update {self.args[0]}.",
                        ephemeral=True,
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
            timestamp=nextcord.utils.utcnow(),
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
        brief="Sends a list of all products.",
        catagory="product",
    )
    async def getproducts(self, ctx):
        dbresponse = getproducts()
        embed = Embed(
            title="Products",
            description=f"Here is all the products I was able to get for this server!",
            colour=ctx.author.colour,
            timestamp=nextcord.utils.utcnow(),
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
        name="retrieve",
        aliases=["retrieveproduct", "getproduct"],
        brief="DM's you the specified product if you own it.",
        catagory="product",
    )
    async def retrieveproduct(self, ctx, *, product: str):
        userinfo = getuserfromdiscord(ctx.author.id)

        if userinfo:
            if product in userinfo["purchases"]:
                embed = Embed(
                    title="Thanks for your purchase!",
                    description=f"Thank you for your purchase of {product} please get it by using the links below.",
                    colour=Colour.from_rgb(255, 255, 255),
                    timestamp=nextcord.utils.utcnow(),
                )

                try:
                    if not ctx.author.dm_channel:
                        await ctx.author.create_dm()

                    await ctx.author.dm_channel.send(embed=embed)

                    for attachment in getproduct(product)["attachments"]:
                        await ctx.author.dm_channel.send(attachment)
                except Forbidden:
                    await ctx.send(
                        "Please open your DM's and try again.", reference=ctx.message
                    )

    @command(
        name="createproduct",
        aliases=["newproduct", "makeproduct"],
        brief="Create a new product.",
        catagory="product",
    )
    @has_permissions(manage_guild=True)
    async def createproduct(self, ctx):
        questions = [
            "What do you want to call this product?",
            "What do you want the description of the product to be?",
            "What do you want the product price to be?",
            "attachments",
        ]
        embedmessages = []
        usermessages = []
        awnsers = []
        attachments = []

        def check(m):
            return m.content and m.author == ctx.author

        def emojicheck(self, user):
            return user == ctx.author

        def attachmentcheck(m):
            return m.author == ctx.author

        for i, question in enumerate(questions):
            if question == "attachments":
                embed = Embed(
                    title=f"Create Product (Question {i+1})",
                    description='Please post any attachments\nSay "Done" when complete',
                    colour=ctx.author.colour,
                    timestamp=nextcord.utils.utcnow(),
                )

                embed.set_footer(
                    text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
                )

                fields = [
                    (
                        "Attachments",
                        "None",
                        False,
                    )
                ]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                embedmessage = await ctx.send(embed=embed)
                embedmessages.append(embedmessage)
                while True:
                    try:
                        message = await self.bot.wait_for(
                            "message", timeout=200.0, check=attachmentcheck
                        )
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
                    if message.content.lower() == "done":
                        usermessages.append(message)
                        break
                    elif not message.attachments == [] and message.attachments:
                        for attachment in message.attachments:
                            attachments.append(attachment.url)
                            embed = Embed(
                                title=f"Create Product (Question {i+1})",
                                description='Please post any attachments\nSay "Done" when complete',
                                colour=ctx.author.colour,
                                timestamp=nextcord.utils.utcnow(),
                            )

                            embed.set_footer(
                                text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
                            )

                            fields = [
                                (
                                    "Attachments",
                                    "\n".join(
                                        [attachment for attachment in attachments]
                                    ),
                                    False,
                                )
                            ]

                            for name, value, inline in fields:
                                embed.add_field(name=name, value=value, inline=inline)

                            embed.set_footer(text="Pembroke Bot • By: parker02311")
                            await embedmessage.edit(embed=embed)
                            await ctx.send(
                                "It is recommended to not delete this message unless needed.",
                                reference=message,
                            )
            else:
                embed = Embed(
                    title=f"Create Product (Question {i+1})",
                    description=question,
                    colour=ctx.author.colour,
                    timestamp=nextcord.utils.utcnow(),
                )
                embed.set_footer(
                    text='Redon Tech RPH • Say "Cancel" to cancel. • By: parker02311'
                )
                embedmessage = await ctx.send(embed=embed)
                embedmessages.append(embedmessage)
                try:
                    message = await self.bot.wait_for(
                        "message", timeout=200.0, check=check
                    )
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
            timestamp=nextcord.utils.utcnow(),
        )

        fields = [
            ("Name", awnsers[0], False),
            ("Description", awnsers[1], False),
            ("Price", awnsers[2], False),
            (
                "Attachments",
                "\n".join([attachment for attachment in attachments]),
                False,
            ),
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
                createproduct(awnsers[0], awnsers[1], awnsers[2], attachments)
            except:
                await ctx.send(
                    "I was unable to create the product...", delete_after=5.0
                )
                raise

            embed = Embed(
                title="Product Created",
                description="The product was successfully created.",
                colour=ctx.author.colour,
                timestamp=nextcord.utils.utcnow(),
            )

            fields = [
                ("Name", awnsers[0], False),
                ("Description", awnsers[1], False),
                ("Price", awnsers[2], False),
                (
                    "Attachments",
                    "\n".join([attachment for attachment in attachments]),
                    False,
                ),
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
        brief="Delete's a product.",
        catagory="product",
    )
    @has_permissions(manage_guild=True)
    async def deleteproduct(self, ctx):
        await ctx.send(
            "Chose a product to delete", view=DeleteView(ctx), reference=ctx.message
        )

    @command(
        name="updateproduct",
        aliases=["changeproduct"],
        brief="Update's a product.",
        catagory="product",
    )
    @has_permissions(manage_guild=True)
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
