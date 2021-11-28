"""
    File: /lib/cogs/user.py
    Info: This cog handles all the commands for user facing commands
"""
import nextcord
from nextcord.ext.commands import Cog, command, has_permissions, Greedy
from nextcord import (
    Embed,
    Colour,
    Member,
    colour,
    ui,
    Interaction,
    SelectOption,
    ButtonStyle,
)
from datetime import datetime
from typing import Optional
from ..utils.api import *
from ..utils.util import (
    AreYouSureView,
    UserNotVerified,
    RequiresVerification,
    UserOwnsProduct,
)


class TransferSelect(ui.Select):
    def __init__(self, user, context, whoto):
        self.user = user
        self.whoto = whoto
        self.context = context
        userinfo = getuserfromdiscord(self.user.id)
        options = []

        for product in userinfo["purchases"]:
            options.append(SelectOption(label=product))

        super().__init__(custom_id="user:transfer_select", options=options)

    async def callback(self, interaction: Interaction):
        product = str(interaction.data["values"])[2:-2]
        view = AreYouSureView(self.context)
        await interaction.message.delete()
        message = await interaction.channel.send(
            embed=Embed(
                title="Are you sure?",
                description=f"Are you sure you want to transfer **{product}** to **{self.whoto.mention}**?",
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
                    description=f"Please wait while we transfer your **{product}**.",
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

                if product in goingto["purchases"]:
                    raise UserOwnsProduct

                revokeproduct(interactor["_id"], product)
                giveproduct(goingto["_id"], product)

                await message.edit(
                    embed=Embed(
                        title="Transfer Complete",
                        description=f"Your **{product}** has been transferred to the selected account.",
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
                        description=f"**{self.whoto.mention}** already owns **{product}**.",
                        colour=Colour.from_rgb(255, 0, 0),
                        timestamp=nextcord.utils.utcnow(),
                    )
                )
            except:
                await message.edit(
                    embed=Embed(
                        title="Transfer Failed",
                        description=f"An error occured while transferring your **{product}**.",
                        colour=Colour.from_rgb(255, 0, 0),
                        timestamp=nextcord.utils.utcnow(),
                    )
                )


class TransferView(ui.View):
    def __init__(self, context, whoto: Member):
        super().__init__(timeout=None)
        self.add_item(TransferSelect(context.author, context, whoto))


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
    async def profile(self, ctx, member: Optional[Member]):
        member = member or ctx.author

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
                    "\n".join([product for product in userinfo["purchases"]]) or "None",
                    True,
                ),
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await ctx.send(embed=embed, reference=ctx.message)
        else:
            await ctx.send(
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
    async def transfer(self, ctx, member: Member):
        await ctx.send(
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
    async def giveproduct(self, ctx, members: Greedy[Member], *, product: str):
        if not len(members):
            await ctx.send(
                f"You left out a vital argument, use {self.bot.PREFIX}help to see all the required arguments.",
                refrence=ctx.message,
            )

        elif not getproduct(product):
            await ctx.send(f"You inputted a incorrect product.", refrence=ctx.message)

        else:
            for member in members:
                data = getuserfromdiscord(member.id)
                if data:
                    try:
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
                        except:
                            await ctx.send(
                                f"I was unable to DM {member.mention} there product.",
                                reference=ctx.message,
                            )
                    except:
                        await ctx.send(
                            f"I was unable to give {member.mention} {product}.",
                            reference=ctx.message,
                        )
                        members.remove(member)
                else:
                    await ctx.send(
                        f"I was unable to give {member.mention} {product}.",
                        reference=ctx.message,
                    )
                    members.remove(member)

            if members:
                await ctx.send(
                    "Gave "
                    + "".join([member.mention for member in members])
                    + f" {product}.",
                    reference=ctx.message,
                )

    @command(
        name="revokeproduct",
        aliases=["remove", "rovoke"],
        brief="Give's a user a product.",
        catagory="user",
    )
    @has_permissions(manage_guild=True)
    async def revokeproduct(self, ctx, members: Greedy[Member], *, product: str):
        if not len(members):
            await ctx.send(
                f"You left out a vital argument, use {self.bot.PREFIX}help to see all the required arguments.",
                refrence=ctx.message,
            )

        elif not getproduct(product):
            await ctx.send(f"You inputted a incorrect product.", refrence=ctx.message)

        else:
            for member in members:
                data = getuserfromdiscord(member.id)
                if data:
                    try:
                        revokeproduct(data["_id"], product)
                    except:
                        await ctx.send(
                            f"I was unable to revoke {member.mention}'s {product}.",
                            reference=ctx.message,
                        )
                        members.remove(member)
                else:
                    await ctx.send(
                        f"I was unable to revoke {member.mention}'s {product}.",
                        reference=ctx.message,
                    )
                    members.remove(member)

            if members:
                await ctx.send(
                    "Revoked "
                    + "".join([member.mention + "'s" for member in members])
                    + f" {product}.",
                    reference=ctx.message,
                )

    @command(
        mame="unlink",
        aliases=["unlinkme", "ul", "unverify", "uv"],
        brief="Unlinks your Roblox account.",
        catagory="user",
    )
    @RequiresVerification()
    async def unlink(self, ctx):
        view = AreYouSureView(ctx)
        message = await ctx.send(
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
                user = getuserfromdiscord(ctx.author.id)
                if not user:
                    raise UserNotVerified

                unlinkuser(user["_id"])
                await message.edit(
                    "Your Roblox account has been unlinked.", embed=None, view=None
                )
            except UserNotVerified:
                await message.edit("You are not verified.", embed=None, view=None)
            except:
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
