"""
    File: /lib/cogs/user.py
    Info: This cog handles all the commands for user facing commands
"""
import nextcord
from nextcord.ext.commands import Cog, has_permissions, Context
from nextcord import (
    Embed,
    Colour,
    Member,
    colour,
    ui,
    Interaction,
    SelectOption,
    ButtonStyle,
    SlashOption,
)
from datetime import datetime
from typing import Optional, Union
from ..utils import (
    AreYouSureView,
    UserNotVerified,
    RequiresVerification,
    UserOwnsProduct,
    getproduct,
    getuserfromdiscord,
    giveproduct,
    revokeproduct,
    unlinkuser,
    command,
    csend,
    channelsend,
    getauthor,
    getproducts,
)

products = [product["name"] for product in getproducts()]


class TransferSelect(ui.Select):
    def __init__(self, user, context, whoto):
        self.user = user
        self.whoto = whoto
        self.context = context
        userinfo = getuserfromdiscord(self.user.id)
        options = []

        for product in userinfo["purchases"]:
            productinfo = getproduct(product)
            options.append(SelectOption(label=productinfo["name"], description=product))

        super().__init__(custom_id="user:transfer_select", options=options)

    async def callback(self, interaction: Interaction):
        product = getproduct(str(interaction.data["values"])[2:-2])
        view = AreYouSureView(self.context)
        await interaction.message.delete()
        message = await channelsend(
            self.context,
            embed=Embed(
                title="Are you sure?",
                description=f"Are you sure you want to transfer **{product['name']}** to **{self.whoto.mention}**?",
                colour=Colour.from_rgb(255, 255, 0),
                timestamp=nextcord.utils.utcnow(),
            ),
            view=view,
            reference=self.context.message,
        )
        await view.wait()

        if view.Return == None:
            await message.edit("Timed Out", embed=None, view=None)
        elif view.Return == False:
            await message.edit("Canceled Transfer", embed=None, view=None)
        elif view.Return == True:
            await message.edit(
                embed=Embed(
                    title="Transferring...",
                    description=f"Please wait while we transfer your **{product['name']}**.",
                    colour=Colour.from_rgb(255, 255, 255),
                    timestamp=nextcord.utils.utcnow(),
                ),
                view=None,
            )

            try:
                interactor = getuserfromdiscord(self.user.id)
                goingto = getuserfromdiscord(self.whoto.id)
                if not goingto:
                    raise UserNotVerified

                if product["_id"] in goingto["purchases"]:
                    raise UserOwnsProduct

                revokeproduct(interactor["_id"], product["name"])
                giveproduct(goingto["_id"], product["name"])

                await message.edit(
                    embed=Embed(
                        title="Transfer Complete",
                        description=f"Your **{product['name']}** has been transferred to the selected account.",
                        colour=Colour.from_rgb(0, 255, 0),
                        timestamp=nextcord.utils.utcnow(),
                    )
                )
            except UserNotVerified:
                await message.edit(
                    embed=Embed(
                        title="Transfer Failed",
                        description=f"**{self.whoto.mention}** is not verified.",
                        colour=Colour.from_rgb(255, 0, 0),
                        timestamp=nextcord.utils.utcnow(),
                    )
                )
            except UserOwnsProduct:
                await message.edit(
                    embed=Embed(
                        title="Transfer Failed",
                        description=f"**{self.whoto.mention}** already owns **{product['name']}**.",
                        colour=Colour.from_rgb(255, 0, 0),
                        timestamp=nextcord.utils.utcnow(),
                    )
                )
            except Exception as e:
                await message.edit(
                    embed=Embed(
                        title="Transfer Failed",
                        description=f"An error occured while transferring your **{product['name']}**.",
                        colour=Colour.from_rgb(255, 0, 0),
                        timestamp=nextcord.utils.utcnow(),
                    )
                )


class TransferView(ui.View):
    def __init__(self, context, whoto: Member):
        super().__init__(timeout=None)
        self.add_item(TransferSelect(getauthor(context), context, whoto))


async def product_autocomplete(self, interaction: Interaction, product: str):
    if not product:
        await interaction.response.send_autocomplete(products)
        return

    get_products = [
        productoption
        for productoption in products
        if productoption.lower().startswith(product.lower())
    ]
    await interaction.response.send_autocomplete(get_products)


class User(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="profile",
        aliases=["me", "userinfo", "whois"],
        brief="Returns info about the specified user.",
        catagory="user",
    )
    @RequiresVerification()
    async def profile(
        self,
        ctx: Union[Context, Interaction],
        member: Optional[Member] = SlashOption(
            name="member", description="The user to get info about.", required=False
        ),
    ):
        member = member or getauthor(ctx)

        userinfo = getuserfromdiscord(member.id)
        if userinfo:
            embed = Embed(
                title=member.display_name,
                description=f"Here is the info on {member.mention}",
                colour=member.colour,
                timestamp=nextcord.utils.utcnow(),
            )

            fields = [
                ("UserID", userinfo["_id"], True),
                ("Username", userinfo["username"], True),
                (
                    "Owned Products",
                    "\n".join(
                        [
                            getproduct(product)["name"]
                            for product in userinfo["purchases"]
                        ]
                    )
                    or "None",
                    True,
                ),
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await csend(ctx, embed=embed, reference=ctx.message)
        else:
            await csend(
                ctx,
                f"I was unable to find any info on {member.display_name}.",
                reference=ctx.message,
            )

    @command(
        name="transfer",
        aliases=["transferproduct"],
        brief="Transfer's a product to another user.",
        catagory="user",
    )
    @RequiresVerification()
    async def transfer(
        self,
        ctx: Union[Context, Interaction],
        member: Member = SlashOption(
            name="member",
            description="The user to transfer the product to.",
            required=True,
        ),
    ):
        await csend(
            ctx,
            embed=Embed(
                title="Transfer Product",
                description="Please select the product you want to transfer.",
                colour=Colour.from_rgb(255, 255, 255),
                timestamp=nextcord.utils.utcnow(),
            ),
            view=TransferView(ctx, member),
            reference=ctx.message,
        )

    @command(
        name="giveproduct",
        aliases=["ammendproduct", "give"],
        brief="Give's a user a product.",
        catagory="user",
    )
    @has_permissions(manage_guild=True)
    async def giveproduct(
        self,
        ctx: Union[Context, Interaction],
        member: Member = SlashOption(
            name="member", description="Members to give the product to."
        ),
        *,
        product: str = SlashOption(
            name="product",
            description="The product to give.",
            autocomplete=True,
            autocomplete_callback=product_autocomplete,
        ),
    ):
        if not member:
            await csend(
                f"You left out a vital argument, use {self.bot.PREFIX}help to see all the required arguments.",
                refrence=ctx.message,
            )

        elif not getproduct(product):
            await csend(f"You inputted a incorrect product.", refrence=ctx.message)

        else:
            data = getuserfromdiscord(member.id)
            if data:
                try:
                    if getproduct(product)["_id"] in data["purchases"]:
                        await csend(
                            ctx,
                            "That user already owns that product.",
                            reference=ctx.message,
                        )
                    else:
                        giveproduct(data["_id"], product)

                        try:
                            embed = Embed(
                                title="Thanks for your purchase!",
                                description=f"Thank you for your purchase of {product} please get it by using the links below.",
                                colour=Colour.from_rgb(255, 255, 255),
                                timestamp=nextcord.utils.utcnow(),
                            )
                            if not member.dm_channel:
                                await member.create_dm()

                            await member.dm_channel.send(embed=embed)

                            for attachment in getproduct(product)["attachments"]:
                                await member.dm_channel.send(attachment)
                        except Exception as e:
                            await csend(
                                ctx,
                                f"I was unable to DM {member.mention} there product.",
                                reference=ctx.message,
                            )

                        await csend(
                            ctx,
                            f"{member.mention} has been given {product}.",
                            reference=ctx.message,
                        )
                except Exception as e:
                    await csend(
                        ctx,
                        f"I was unable to give {member.mention} {product}.",
                        reference=ctx.message,
                    )
            else:
                await csend(
                    ctx,
                    f"I was unable to give {member.mention} {product}.",
                    reference=ctx.message,
                )

    @command(
        name="revokeproduct",
        aliases=["remove", "rovoke"],
        brief="Give's a user a product.",
        catagory="user",
    )
    @has_permissions(manage_guild=True)
    async def revokeproduct(
        self,
        ctx: Union[Context, Interaction],
        member: Member = SlashOption(
            name="member", description="Members to give the product to."
        ),
        *,
        product: str = SlashOption(
            name="product",
            description="The product to give.",
            autocomplete=True,
            autocomplete_callback=product_autocomplete,
        ),
    ):
        if not member:
            await csend(
                ctx,
                f"You left out a vital argument, use {self.bot.PREFIX}help to see all the required arguments.",
                refrence=ctx.message,
            )

        elif not getproduct(product):
            await csend(ctx, f"You inputted a incorrect product.", refrence=ctx.message)

        else:
            data = getuserfromdiscord(member.id)
            if data:
                try:
                    revokeproduct(data["_id"], product)

                    await csend(
                        ctx,
                        f"{member.mention} {product} has been revoked.",
                        reference=ctx.message,
                    )
                except Exception as e:
                    await csend(
                        ctx,
                        f"I was unable to revoke {member.mention}'s {product}.",
                        reference=ctx.message,
                    )
            else:
                await csend(
                    ctx,
                    f"I was unable to revoke {member.mention}'s {product}.",
                    reference=ctx.message,
                )

    @command(
        name="unlink",
        aliases=["unlinkme", "ul", "unverify", "uv"],
        brief="Unlinks your Roblox account.",
        catagory="user",
    )
    @RequiresVerification()
    async def unlink(self, ctx: Union[Context, Interaction]):
        author = getauthor(ctx)
        view = AreYouSureView(ctx)
        message = await csend(
            ctx,
            embed=Embed(
                title="Are you sure?",
                description="Are you sure you want to unlink your Roblox account?",
                colour=Colour.from_rgb(255, 255, 255),
                timestamp=nextcord.utils.utcnow(),
            ),
            view=view,
            reference=ctx.message,
        )
        await view.wait()

        if view.Return == None:
            await message.edit("Timed Out", embed=None, view=None)
        elif view.Return == False:
            await message.edit("Cancelled", embed=None, view=None)
        elif view.Return == True:
            try:
                user = getuserfromdiscord(author.id)
                if not user:
                    raise UserNotVerified

                unlinkuser(user["_id"])
                await message.edit(
                    "Your Roblox account has been unlinked.", embed=None, view=None
                )
            except UserNotVerified:
                await message.edit("You are not verified.", embed=None, view=None)
            except Exception as e:
                await message.edit(
                    "I was unable to unlink your account.", embed=None, view=None
                )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("user")
            await self.bot.stdout.send("`/lib/cogs/user.py` ready")
            print(" /lib/cogs/user.py ready")


def setup(bot):
    bot.add_cog(User(bot))
