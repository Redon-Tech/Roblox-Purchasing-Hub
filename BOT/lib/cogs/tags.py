"""
    File: /lib/cogs/tags.py
    Info: This cog handles all commands related to tags
"""
import nextcord
from nextcord import SlashOption
from nextcord.ext.commands import Cog, has_permissions, Context
from nextcord import Embed, Colour, ui, Interaction, SelectOption, ButtonStyle
from ..utils import (
    AreYouSureView,
    gettags,
    gettag,
    createtag,
    updatetag,
    deletetag,
    command,
    csend,
    channelsend,
    getauthor,
)
from typing import Union

tagoptions = []

# Cancel Button
class CancelView(ui.View):
    def __init__(self, context):
        super().__init__(timeout=None)
        self.context = context
        self.canceled = False

    @ui.button(label="Cancel", style=ButtonStyle.danger, custom_id="tags:cancel")
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
        global tagoptions
        tagoptions.clear()
        for tag in gettags():
            tagoptions.append(
                SelectOption(label=tag["name"], description=str(tag["color"]))
            )

    @ui.select(
        custom_id="tags:delete_select",
        options=tagoptions,
    )
    async def delete_select(self, _, interaction: Interaction):

        tag = str(interaction.data["values"])[2:-2]
        await interaction.message.delete()
        view = AreYouSureView(self.context)
        message = await channelsend(
            self.context,
            f"Are you sure you would like to delete {tag}?",
            view=view,
            reference=self.context.message,
        )
        await view.wait()

        if view.Return == None:
            await message.delete()
            await interaction.response.send_message("Timed Out", ephemeral=True)
        elif view.Return == False:
            await message.delete()
            await interaction.response.send_message("Canceled Delete", ephemeral=True)
        elif view.Return == True:
            try:
                deletetag(tag)
                await message.delete()
                await interaction.response.send_message(
                    f"Deleted {tag}.",
                    ephemeral=True,
                )
            except Exception as e:
                await message.delete()
                await interaction.response.send_message(
                    f"Failed to delete {tag}.",
                    ephemeral=True,
                )


# Update View's


def Update_Tag(Product, Key, Value):
    if Key == "name":
        updatetag(Product["name"], Value, Product["color"], Product["textcolor"])
    else:
        Product[Key] = Value
        updatetag(
            Product["name"], Product["name"], Product["color"], Product["textcolor"]
        )


## What to update
class WhatUpdateView(ui.View):
    def __init__(self, context, tag, bot):
        super().__init__(timeout=600.0)
        self.context = context
        self.tag = gettag(tag)
        self.bot = bot

    @ui.button(label="Name", style=ButtonStyle.primary, custom_id="tags:update_name")
    async def update_name(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.tag['name']}",
            description=f"What would you like to change the name to?",
            colour=Colour.blue(),
            timestamp=nextcord.utils.utcnow(),
        )
        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.context.author

        try:
            message = await self.bot.wait_for("message", timeout=600.0, check=check)
        except TimeoutError:
            await interaction.message.delete()
            await csend(
                self.context,
                "Timed Out",
                reference=self.context.message,
                delete_after=5.0,
            )
            self.stop()

        if not message is None and view.canceled is False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await csend(
                    self.context,
                    "Canceled",
                    reference=self.context.message,
                    delete_after=5.0,
                )
                self.stop()
            else:
                await interaction.message.delete()
                view = AreYouSureView(self.context)
                are_u_sure_message = await csend(
                    self.context,
                    f"Are you sure you would like to change `{self.tag['name']}` to `{message.content}`?",
                    view=view,
                    reference=self.context.message,
                )
                await view.wait()
                await are_u_sure_message.delete()

                if view.Return == None:
                    await message.delete()
                    await csend(
                        self.context,
                        "Timed out",
                        reference=self.context.message,
                        delete_after=5.0,
                    )
                elif view.Return == False:
                    await message.delete()
                    await csend(
                        self.context,
                        "Canceled update",
                        reference=self.context.message,
                        delete_after=5.0,
                    )
                elif view.Return == True:
                    try:
                        Update_Tag(self.tag, "name", message.content)
                        await message.delete()
                        name = self.tag["name"]
                        await csend(
                            self.context,
                            f"Updated {name}.",
                            reference=self.context.message,
                            delete_after=5.0,
                        )
                    except Exception as e:
                        await message.delete()
                        await csend(
                            self.context,
                            f"Failed to update {self.tag}.",
                            reference=self.context.message,
                            delete_after=5.0,
                        )

    @ui.button(
        label="Color",
        style=ButtonStyle.primary,
        custom_id="tags:update_color",
    )
    async def update_color(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.tag['name']}",
            description=f"What would you like to change the color to? (Format: `r, g, b`)",
            colour=Colour.blue(),
            timestamp=nextcord.utils.utcnow(),
        )
        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.context.author

        try:
            message = await self.bot.wait_for("message", timeout=600.0, check=check)
        except TimeoutError:
            await interaction.message.delete()
            await csend(
                self.context,
                "Timed Out",
                reference=self.context.message,
                delete_after=5.0,
            )
            self.stop()

        if not message is None and view.canceled is False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await csend(
                    self.context,
                    "Canceled",
                    reference=self.context.message,
                    delete_after=5.0,
                )
                self.stop()
            else:
                if len(message.content.split(", ")) != 3:
                    await interaction.message.delete()
                    await csend(
                        self.context,
                        "Invalid Color Canceled. Please use the format `r, g, b`",
                        reference=self.context.message,
                        delete_after=5.0,
                    )
                    self.stop()
                await interaction.message.delete()
                view = AreYouSureView(self.context)
                are_u_sure_message = await csend(
                    self.context,
                    f"Are you sure you would like to change `{self.tag['color']}` to `{message.content}`?",
                    view=view,
                    reference=self.context.message,
                )
                await view.wait()
                await are_u_sure_message.delete()

                if view.Return == None:
                    await message.delete()
                    await csend(
                        self.context,
                        "Timed out",
                        reference=self.context.message,
                        delete_after=5.0,
                    )
                elif view.Return == False:
                    await message.delete()
                    await csend(
                        self.context,
                        "Canceled update",
                        reference=self.context.message,
                        delete_after=5.0,
                    )
                elif view.Return == True:
                    try:
                        colors = message.content.split(", ")
                        for i in range(len(colors)):
                            colors[i] = int(colors[i])
                        Update_Tag(self.tag, "color", colors)
                        await message.delete()
                        name = self.tag["name"]
                        await csend(
                            self.context,
                            f"Updated {name}.",
                            reference=self.context.message,
                            delete_after=5.0,
                        )
                    except Exception as e:
                        await message.delete()
                        await csend(
                            self.context,
                            f"Failed to update {self.tag}.",
                            reference=self.context.message,
                            delete_after=5.0,
                        )

    @ui.button(
        label="Text Color", style=ButtonStyle.primary, custom_id="tags:update_textcolor"
    )
    async def update_textcolor(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.tag['name']}",
            description=f"What would you like to change the text color to? (Format: `r, g, b`)",
            colour=Colour.blue(),
            timestamp=nextcord.utils.utcnow(),
        )
        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.context.author

        try:
            message = await self.bot.wait_for("message", timeout=600.0, check=check)
        except TimeoutError:
            await interaction.message.delete()
            await csend(
                self.context,
                "Timed Out",
                reference=self.context.message,
                delete_after=5.0,
            )
            self.stop()

        if not message is None and view.canceled is False:
            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await csend(
                    self.context,
                    "Canceled",
                    reference=self.context.message,
                    delete_after=5.0,
                )
                self.stop()
            else:
                if len(message.content.split(", ")) != 3:
                    await interaction.message.delete()
                    await csend(
                        self.context,
                        "Invalid Color Canceled. Please use the format `r, g, b`",
                        reference=self.context.message,
                        delete_after=5.0,
                    )
                    self.stop()
                await interaction.message.delete()
                view = AreYouSureView(self.context)
                are_u_sure_message = await csend(
                    self.context,
                    f"Are you sure you would like to change `{self.tag['textcolor']}` to `{str(message.content)}`?",
                    view=view,
                    reference=self.context.message,
                )
                await view.wait()
                await are_u_sure_message.delete()

                if view.Return == None:
                    await message.delete()
                    await csend(
                        self.context,
                        "Timed out",
                        reference=self.context.message,
                        delete_after=5.0,
                    )
                elif view.Return == False:
                    await message.delete()
                    await csend(
                        self.context,
                        "Canceled update",
                        reference=self.context.message,
                        delete_after=5.0,
                    )
                elif view.Return == True:
                    try:
                        colors = message.content.split(", ")
                        for i in range(len(colors)):
                            colors[i] = int(colors[i])
                        Update_Tag(self.tag, "textcolor", colors)
                        await message.delete()
                        name = self.tag["name"]
                        await csend(
                            self.context,
                            f"Updated {name}.",
                            reference=self.context.message,
                            delete_after=5.0,
                        )
                    except Exception as e:
                        await message.delete()
                        await csend(
                            self.context,
                            f"Failed to update {self.tag}.",
                            reference=self.context.message,
                            delete_after=5.0,
                        )

    @ui.button(label="cancel", style=ButtonStyle.danger, custom_id="tags:update_cancel")
    async def update_cancel(self, _, interaction: Interaction):
        await interaction.message.delete()
        await csend(
            self.context, "Canceled", reference=self.context.message, delete_after=5.0
        )
        self.stop()


## Initial View
class InitialUpdateView(ui.View):
    def __init__(self, context, bot):
        super().__init__(timeout=600.0)
        self.context = context
        self.bot = bot
        global tagoptions
        tagoptions.clear()
        for tag in gettags():
            tagoptions.append(
                SelectOption(label=tag["name"], description=str(tag["color"]))
            )

    @ui.select(
        custom_id="tags:update_select",
        options=tagoptions,
    )
    async def update_select(self, _, interaction: Interaction):
        tag = str(interaction.data["values"])[2:-2]
        embed = Embed(
            title=f"Update {tag}",
            description=f"What would you like to change?",
            colour=Colour.blue(),
            timestamp=nextcord.utils.utcnow(),
        )
        embed.set_footer(text="Redon Hub • By: parker02311")
        await interaction.message.edit(
            "", embed=embed, view=WhatUpdateView(self.context, tag, self.bot)
        )


class Tags(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="tags",
        aliases=["listtags", "viewtags", "alltags"],
        brief="Sends a list of all tags.",
        catagory="tag",
    )
    async def gettags(self, ctx: Union[Context, Interaction]):
        author = getauthor(ctx)
        dbresponse = gettags()
        embed = Embed(
            title="Products",
            description=f"Here is all the tags I was able to get for this server!",
            colour=author.colour,
            timestamp=nextcord.utils.utcnow(),
        )

        fields = []

        for tag in dbresponse:
            fields.append(
                (
                    tag["name"],
                    f"Color: {tag['color']}\nText Color: {tag['textcolor']}",
                    False,
                )
            )

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text="Redon Hub • By: parker02311")

        await csend(ctx, embed=embed, reference=ctx.message)

    @command(
        name="createtag",
        aliases=["newtag", "maketag"],
        brief="Create a new tag.",
        catagory="tag",
    )
    @has_permissions(manage_guild=True)
    async def createtag(self, ctx: Union[Context, Interaction]):
        author = getauthor(ctx)
        questions = [
            "What do you want to tittle your tag?",
            "What do you want the tag color to be? (Format: `r, g, b`)",
            "What do you want the tags text to be? (Format: `r, g, b`)",
        ]
        embedmessages = []
        usermessages = []
        awnsers = []

        def check(m):
            return m.content and m.author == author

        def emojicheck(self, user):
            return user == author

        for i, question in enumerate(questions):
            embed = Embed(
                title=f"Create Tag (Question {i+1})",
                description=question,
                colour=author.colour,
                timestamp=nextcord.utils.utcnow(),
            )
            embed.set_footer(
                text='Redon Hub • Say "Cancel" to cancel. • By: parker02311'
            )
            embedmessage = await csend(ctx, embed=embed)
            embedmessages.append(embedmessage)
            try:
                message = await self.bot.wait_for("message", timeout=200.0, check=check)
            except TimeoutError:
                await csend(ctx, "You didn't answer the questions in Time")
                return
            if message.content.lower() == "cancel":
                usermessages.append(message)
                for message in embedmessages:
                    await message.delete()

                for message in usermessages:
                    await message.delete()

                await ctx.message.delete()
                await csend(ctx, "Canceled", delete_after=5.0)

                break
            else:
                if i != 0:
                    if len(message.content.split(", ")) != 3:
                        usermessages.append(message)
                        for message in embedmessages:
                            await message.delete()

                        for message in usermessages:
                            await message.delete()

                        await ctx.message.delete()
                        await csend(
                            ctx,
                            "Invalid Color Canceled. Please use the format `r, g, b`",
                            delete_after=5.0,
                        )
                        return
                usermessages.append(message)
                awnsers.append(message.content)

        lastbeforefinal = await csend(
            ctx, "Creating final message this may take a moment."
        )

        for message in embedmessages:
            await message.delete()

        for message in usermessages:
            await message.delete()

        embed = Embed(
            title="Confirm Tag Creation",
            description="✅ to confirm\n❌ to cancel",
            colour=author.colour,
            timestamp=nextcord.utils.utcnow(),
        )

        fields = [
            ("Tittle", awnsers[0], False),
            ("Color", awnsers[1], False),
            ("Text Color", awnsers[2], False),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text="Redon Hub • By: parker02311")
        finalmessage = await csend(ctx, embed=embed)
        await finalmessage.add_reaction("✅")
        await finalmessage.add_reaction("❌")
        await lastbeforefinal.delete()

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=200.0, check=emojicheck
            )
        except TimeoutError:
            await csend(ctx, "You didn't answer the questions in Time")
            return

        if str(reaction.emoji) == "✅":
            try:
                createtag(
                    awnsers[0],
                    list(map(int, awnsers[1].split(", "))),
                    list(map(int, awnsers[2].split(", "))),
                )
            except Exception as e:
                await csend(ctx, "I was unable to create the tag...", delete_after=5.0)
                raise

            embed = Embed(
                title="Tag Created",
                description="The tag was successfully created.",
                colour=author.colour,
                timestamp=nextcord.utils.utcnow(),
            )

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            embed.set_footer(text="Redon Hub • By: parker02311")
            await csend(ctx, embed=embed)
            await finalmessage.delete()
            await ctx.message.delete()

    @command(
        name="deletetag",
        aliases=["removetag", "terminatetag", "fuckoffpieceofshittag"],
        brief="Delete's a tag.",
        catagory="tag",
    )
    @has_permissions(manage_guild=True)
    async def deletetag(self, ctx: Union[Context, Interaction]):
        await csend(
            ctx, "Chose a tag to delete", view=DeleteView(ctx), reference=ctx.message
        )

    @command(
        name="updatetag",
        aliases=["changetag"],
        brief="Update's a tag.",
        catagory="tag",
    )
    @has_permissions(manage_guild=True)
    async def updatetag(self, ctx: Union[Context, Interaction]):
        await csend(
            ctx,
            "Chose a tag to update.",
            view=InitialUpdateView(ctx, self.bot),
            reference=ctx.message,
        )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("tags")
            await self.bot.stdout.send("`/lib/cogs/tags.py` ready")
            print(" /lib/cogs/tags.py ready")


def setup(bot):
    bot.add_cog(Tags(bot))
