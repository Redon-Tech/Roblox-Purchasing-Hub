"""
    File: /lib/cogs/user.py
    Info: This cog handles all the commands for user facing commands
"""
import nextcord
from nextcord.ext.commands import Cog, command, has_permissions, Greedy
from nextcord import Embed, Colour, Member, colour
from datetime import datetime
from typing import Optional
from ..utils.api import *


class User(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="profile",
        aliases=["me", "userinfo", "whois"],
        brief="Returns info about the specified user.",
        catagory="user",
    )
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
                                f"I was unable to DM {member.mention} there product."
                            )
                    except:
                        await ctx.send(
                            f"I was unable to give {member.mention} {product}."
                        )
                        members.remove(member)
                else:
                    await ctx.send(f"I was unable to give {member.mention} {product}.")
                    members.remove(member)

            if members:
                await ctx.send(
                    "Gave "
                    + "".join([member.mention for member in members])
                    + f" {product}."
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
                            f"I was unable to revoke {member.mention}'s {product}."
                        )
                        members.remove(member)
                else:
                    await ctx.send(
                        f"I was unable to revoke {member.mention}'s {product}."
                    )
                    members.remove(member)

            if members:
                await ctx.send(
                    "Revoked "
                    + "".join([member.mention + "'s" for member in members])
                    + f" {product}."
                )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("user")
            await self.bot.stdout.send("`/lib/cogs/user.py` ready")
            print(" /lib/cogs/user.py ready")


def setup(bot):
    bot.add_cog(User(bot))
