"""
    File: /lib/cogs/product.py
    Info: This cog handles all commands related to products
"""
import nextcord
from nextcord import SlashOption
from nextcord.errors import Forbidden
from nextcord.ext.commands import Cog, has_permissions, Context
from nextcord.ext.menus import ListPageSource, ButtonMenuPages, MenuPaginationButton
from nextcord import Embed, Colour, ui, Interaction, SelectOption, ButtonStyle
from typing import Union
from ..utils import (
    AreYouSureView,
    csend,
    getauthor,
    channelsend,
    command,
    getproducts,
    createproduct,
    updateproduct,
    deleteproduct,
    getproduct,
    gettag,
    getuserfromdiscord,
    menustart,
)

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
        view = AreYouSureView(self.context)
        message = await channelsend(
            interaction,
            f"Are you sure you would like to delete {product}?",
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
                deleteproduct(product)
                await message.delete()
                await interaction.response.send_message(
                    f"Deleted {product}.",
                    ephemeral=True,
                )
            except Exception as e:
                await message.delete()
                await interaction.response.send_message(
                    f"Failed to delete {product}.",
                    ephemeral=True,
                )


# Update View's


def Update_Product(Product, Key, Value):
    if Key == "name":
        updateproduct(
            Product["name"],
            Value,
            Product["description"],
            Product["price"],
            Product["productid"],
            Product["attachments"],
            Product["tags"],
            Product["purchases"],
        )
    else:
        Product[Key] = Value
        updateproduct(
            Product["name"],
            Product["name"],
            Product["description"],
            Product["price"],
            Product["productid"],
            Product["attachments"],
            Product["tags"],
            Product["purchases"],
        )


## What to update
class WhatUpdateView(ui.View):
    def __init__(self, context, product, bot):
        super().__init__(timeout=600.0)
        self.context = context
        self.product = getproduct(product)
        self.author = getauthor(context)
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
        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.author

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
                    f"Are you sure you would like to change `{self.product['name']}` to `{message.content}`?",
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
                        Update_Product(self.product, "name", message.content)
                        await message.delete()
                        name = self.product["name"]
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
                            f"Failed to update {name}.",
                            reference=self.context.message,
                            delete_after=5.0,
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
        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.author

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
                    f"Are you sure you would like to change `{self.product['description']}` to `{message.content}`?",
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
                        Update_Product(self.product, "description", message.content)
                        await message.delete()
                        name = self.product["name"]
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
                            f"Failed to update {name}.",
                            reference=self.context.message,
                            delete_after=5.0,
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
        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.author

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
                    f"Are you sure you would like to change `{self.product['price']}` to `{int(message.content)}`?",
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
                        Update_Product(self.product, "price", int(message.content))
                        await message.delete()
                        name = self.product["name"]
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
                            f"Failed to update {name}.",
                            reference=self.context.message,
                            delete_after=5.0,
                        )

    @ui.button(
        label="Product ID",
        style=ButtonStyle.primary,
        custom_id="products:update_productid",
    )
    async def update_productid(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.product['name']}",
            description=f"What would you like to change the product ID to?",
            colour=Colour.blue(),
            timestamp=nextcord.utils.utcnow(),
        )
        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')
        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.content and m.author == self.author

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
                    f"Are you sure you would like to change `{self.product['productid']}` to `{int(message.content)}`?",
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
                        Update_Product(self.product, "productid", int(message.content))
                        await message.delete()
                        name = self.product["name"]
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
                            f"Failed to update {name}.",
                            reference=self.context.message,
                            delete_after=5.0,
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

        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')

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
            return m.author == self.author

        attachments = []

        while True:
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

            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await csend(
                    self.context,
                    "Canceled",
                    reference=self.context.message,
                    delete_after=5.0,
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
                        text='Redon Hub • Say "Cancel" to cancel. • By: parker02311'
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

                    embed.set_footer(text="Redon Hub • By: parker02311")
                    await interaction.message.edit("", embed=embed, view=None)
                    await csend(
                        self.context,
                        "It is recommended to not delete this message unless needed.",
                        reference=message,
                    )

        if attachments:
            await interaction.message.delete()
            view = AreYouSureView(self.context)
            are_u_sure_message = await csend(
                self.context,
                f"Are you sure you would like to change `{self.product['attachments']}` to `{attachments}`?",
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
                    Update_Product(self.product, "attachments", attachments)
                    await message.delete()
                    name = self.product["name"]
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
                        f"Failed to update {name}.",
                        reference=self.context.message,
                        delete_after=5.0,
                    )

    @ui.button(
        label="Tags",
        style=ButtonStyle.primary,
        custom_id="products:update_tags",
    )
    async def update_tags(self, _, interaction: Interaction):
        embed = Embed(
            title=f"Update {self.product['name']}",
            description=f'Please send the tags now. Say "Done" when you are done.',
            colour=Colour.blue(),
            timestamp=nextcord.utils.utcnow(),
        )

        embed.set_footer(text='Redon Hub • Say "Cancel" to cancel. • By: parker02311')

        fields = [
            (
                "Tags",
                "None",
                False,
            )
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        view = CancelView(self.context)
        await interaction.message.edit("", embed=embed, view=None)

        def check(m):
            return m.author == self.author

        tags = []

        while True:
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

            if message.content.lower() == "cancel":
                await interaction.message.delete()
                await csend(
                    self.context,
                    "Canceled",
                    reference=self.context.message,
                    delete_after=5.0,
                )

                break
            if message.content.lower() == "done":
                break
            elif message.content:
                if not gettag(message.content):
                    await message.delete()
                    await self.context.send(
                        "Invalid Tag",
                        delete_after=5.0,
                    )
                else:
                    tags.append(message.content)
                    embed = Embed(
                        title=f"Update {self.product['name']}",
                        description=f'Please send the tags now. Say "Done" when you are done.',
                        colour=Colour.blue(),
                        timestamp=nextcord.utils.utcnow(),
                    )

                    embed.set_footer(
                        text='Redon Hub • Say "Cancel" to cancel. • By: parker02311'
                    )

                    fields = [
                        (
                            "Tags",
                            "\n".join([tag for tag in tags]),
                            False,
                        )
                    ]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    embed.set_footer(text="Redon Hub • By: parker02311")
                    await interaction.message.edit("", embed=embed, view=None)
                    await message.delete()

        if tags:
            await interaction.message.delete()
            view = AreYouSureView(self.context)
            are_u_sure_message = await csend(
                self.context,
                f"Are you sure you would like to change `{self.product['tags']}` to `{tags}`?",
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
                    Update_Product(self.product, "tags", tags)
                    await message.delete()
                    name = self.product["name"]
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
                        f"Failed to update {name}.",
                        reference=self.context.message,
                        delete_after=5.0,
                    )

    @ui.button(
        label="cancel", style=ButtonStyle.danger, custom_id="products:update_cancel"
    )
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
        embed.set_footer(text="Redon Hub • By: parker02311")
        await interaction.message.edit(
            "", embed=embed, view=WhatUpdateView(self.context, product, self.bot)
        )


# Product Page


class ProductPageButton(ui.Button):
    def __init__(self, menu, buttontype):
        super().__init__(label=buttontype, style=ButtonStyle.primary)
        self.menu = menu
        self.buttontype = buttontype

    async def callback(self, interaction: Interaction):
        if self.buttontype == "Next":
            await self.menu.go_to_next_page()
        elif self.buttontype == "Previous":
            await self.menu.go_to_previous_page()


class ProductPageView(ListPageSource):
    def __init__(self, bot, author, data):
        self.bot = bot
        self.data = data
        self.author = author
        super().__init__(data, per_page=2)

    async def write_page(self, menu, products):
        offset = (menu.current_page * self.per_page) + 1
        length = len(self.data)

        embed = Embed(
            title=f"Products",
            description=f"To get more information on a product run `{self.bot.PREFIX}product (product)`!\n\n"
            + "\n".join([product for product in products]),
            colour=self.author.colour,
            timestamp=nextcord.utils.utcnow(),
        )

        embed.set_footer(
            text=f"Redon Hub • {offset:,} - {min(length, offset+self.per_page-1):,} of {length:,} Products • By: parker02311"
        )

        return embed

    async def format_page(self, menu: ButtonMenuPages, entries):
        assert self.per_page != 1, "Cannot have less then 2 products per page"
        products = []

        for product in entries:
            products.append(product["name"])

        menu.clear_items()
        menu.add_item(
            ProductPageButton(menu, "Previous"),
        )
        menu.add_item(
            ProductPageButton(menu, "Next"),
        )

        max_pages = self.get_max_pages()
        for child in menu.children:
            if isinstance(child, nextcord.ui.Button):
                if str(child.label) == "Previous":
                    child.disabled = menu.current_page == 0
                elif max_pages and str(child.label) == "Next":
                    child.disabled = menu.current_page == max_pages - 1

        return {"embed": await self.write_page(menu, products), "view": menu}


class Product(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="products",
        aliases=["listproducts", "viewproducts", "allproducts"],
        brief="Sends a list of all products.",
        catagory="product",
    )
    async def getproducts(self, ctx: Union[Context, Interaction]):
        author = getauthor(ctx)
        dbresponse = getproducts()

        menu = ButtonMenuPages(
            source=ProductPageView(self.bot, author, dbresponse),
            timeout=60.0,
            style=nextcord.ButtonStyle.primary,
        )
        await menustart(menu, ctx)

    @command(
        name="product",
        aliases=["viewproduct", "getproductinfo", "productinfo"],
        brief="Sends information on a product.",
        catagory="product",
    )
    async def getproduct(
        self,
        ctx: Union[Context, Interaction],
        *,
        product: str = SlashOption(
            name="product", description="The product name", required=True
        ),
    ):
        author = getauthor(ctx)
        dbresponse = getproduct(product)

        if dbresponse == None:
            await csend(
                ctx,
                f"{product} is not a valid product.",
                reference=ctx.message,
                delete_after=5.0,
            )
            return

        embed = Embed(
            title=dbresponse["name"],
            description=dbresponse["description"],
            colour=author.colour,
            timestamp=nextcord.utils.utcnow(),
        )
        embed.add_field(name="Price", value=str(dbresponse["price"]), inline=False)
        embed.add_field(
            name="Tags",
            value=", ".join([tag for tag in dbresponse["tags"]]),
            inline=False,
        )

        embed.set_footer(text=f"Redon Hub • By: parker02311")

        await csend(
            ctx,
            embed=embed,
            reference=ctx.message,
        )

    @command(
        name="retrieve",
        aliases=["retrieveproduct", "getproduct"],
        brief="DM's you the specified product if you own it.",
        catagory="product",
    )
    async def retrieveproduct(
        self,
        ctx: Union[Context, Interaction],
        *,
        product: str = SlashOption(
            name="product", description="The product name", required=True
        ),
    ):
        actualproduct = getproduct(product)
        author = getauthor(ctx)
        userinfo = getuserfromdiscord(author.id)

        if userinfo:
            if (
                actualproduct["name"] in userinfo["purchases"]
                or actualproduct["_id"] in userinfo["purchases"]
            ):
                embed = Embed(
                    title="Thanks for your purchase!",
                    description=f"Thank you for your purchase of **{product}** please get it by using the links below.",
                    colour=Colour.from_rgb(255, 255, 255),
                    timestamp=nextcord.utils.utcnow(),
                )

                try:
                    if not author.dm_channel:
                        await author.create_dm()

                    await author.dm_channel.send(embed=embed)

                    for attachment in getproduct(product)["attachments"]:
                        await author.dm_channel.send(attachment)

                    await csend(
                        ctx,
                        "I have sent you a DM with the product.",
                        reference=ctx.message,
                    )
                except Exception as e:
                    if e == Forbidden:
                        await csend(
                            ctx,
                            "Please open your DM's and try again.",
                            reference=ctx.message,
                        )
                    else:
                        raise e

    @command(
        name="createproduct",
        aliases=["newproduct", "makeproduct"],
        brief="Create a new product.",
        catagory="product",
    )
    @has_permissions(manage_guild=True)
    async def createproduct(self, ctx: Union[Context, Interaction]):
        author = getauthor(ctx)
        questions = [
            "What do you want to call this product?",
            "What do you want the description of the product to be?",
            "What do you want the product price to be?",
            "What is the id of the developer product?",
            "attachments",
            "tags",
        ]
        embedmessages = []
        usermessages = []
        awnsers = []
        attachments = []
        tags = []

        def check(m):
            return m.content and m.author == author

        def emojicheck(self, user):
            return user == author

        def attachmentcheck(m):
            return m.author == author

        for i, question in enumerate(questions):
            if question == "attachments":
                embed = Embed(
                    title=f"Create Product (Question {i+1})",
                    description='Please post any attachments\nSay "Done" when complete',
                    colour=author.colour,
                    timestamp=nextcord.utils.utcnow(),
                )

                embed.set_footer(
                    text='Redon Hub • Say "Cancel" to cancel. • By: parker02311'
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

                        if type(ctx) == Context:
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
                                colour=author.colour,
                                timestamp=nextcord.utils.utcnow(),
                            )

                            embed.set_footer(
                                text='Redon Hub • Say "Cancel" to cancel. • By: parker02311'
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

                            embed.set_footer(text="Redon Hub • By: parker02311")
                            await embedmessage.edit(embed=embed)
                            await csend(
                                "It is recommended to not delete this message unless needed.",
                                reference=message,
                            )
            elif question == "tags":
                embed = Embed(
                    title=f"Create Product (Question {i+1})",
                    description='Please send any tags\nSay "Done" when complete',
                    colour=author.colour,
                    timestamp=nextcord.utils.utcnow(),
                )

                embed.set_footer(
                    text='Redon Hub • Say "Cancel" to cancel. • By: parker02311'
                )

                fields = [
                    (
                        "Tags",
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

                        if type(ctx) == Context:
                            await ctx.message.delete()
                        await ctx.send("Canceled", delete_after=5.0)

                        break
                    if message.content.lower() == "done":
                        usermessages.append(message)
                        break
                    elif message.content:
                        tags.append(message.content)
                        embed = Embed(
                            title=f"Create Product (Question {i+1})",
                            description='Please send any tags\nSay "Done" when complete',
                            colour=author.colour,
                            timestamp=nextcord.utils.utcnow(),
                        )

                        embed.set_footer(
                            text='Redon Hub • Say "Cancel" to cancel. • By: parker02311'
                        )

                        fields = [
                            (
                                "Tags",
                                "\n".join([tag for tag in tags]),
                                False,
                            )
                        ]

                        for name, value, inline in fields:
                            embed.add_field(name=name, value=value, inline=inline)

                        embed.set_footer(text="Redon Hub • By: parker02311")
                        await embedmessage.edit(embed=embed)
                        await message.delete()
            else:
                embed = Embed(
                    title=f"Create Product (Question {i+1})",
                    description=question,
                    colour=author.colour,
                    timestamp=nextcord.utils.utcnow(),
                )
                embed.set_footer(
                    text='Redon Hub • Say "Cancel" to cancel. • By: parker02311'
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

                    if type(ctx) == Context:
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
            colour=author.colour,
            timestamp=nextcord.utils.utcnow(),
        )

        fields = [
            ("Name", awnsers[0], False),
            ("Description", awnsers[1], False),
            ("Price", awnsers[2], False),
            ("Developer Product", awnsers[3], False),
            (
                "Attachments",
                "\n".join([attachment for attachment in attachments]) or "None",
                False,
            ),
            (
                "Tags",
                "\n".join([tag for tag in tags]) or "None",
                False,
            ),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text="Redon Hub • By: parker02311")
        finalmessage = await ctx.send(embed=embed)
        await finalmessage.add_reaction("✅")
        await finalmessage.add_reaction("❌")
        await lastbeforefinal.delete()

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=200.0, check=emojicheck
            )
        except TimeoutError:
            await ctx.send("You didn't respond in time.", delete_after=5.0)
            return

        if str(reaction.emoji) == "✅":
            try:
                createproduct(
                    awnsers[0], awnsers[1], awnsers[2], awnsers[3], attachments, tags, 0
                )
            except Exception as e:
                await ctx.send(
                    "I was unable to create the product...", delete_after=5.0
                )
                raise

            embed = Embed(
                title="Product Created",
                description="The product was successfully created.",
                colour=author.colour,
                timestamp=nextcord.utils.utcnow(),
            )

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            embed.set_footer(text="Redon Hub • By: parker02311")
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
    async def deleteproduct(self, ctx: Union[Context, Interaction]):
        await csend(
            ctx,
            "Chose a product to delete",
            view=DeleteView(ctx),
            reference=ctx.message,
        )

    @command(
        name="updateproduct",
        aliases=["changeproduct"],
        brief="Update's a product.",
        catagory="product",
    )
    @has_permissions(manage_guild=True)
    async def updateproduct(self, ctx: Union[Context, Interaction]):
        await csend(
            ctx,
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
