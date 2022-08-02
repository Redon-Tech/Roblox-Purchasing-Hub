"""
    File: /lib/utils/util.py
    Info: Standard utilility file.
"""
from typing import Union
from fastapi import Request
from nextcord import ui, Interaction, SelectOption, ButtonStyle
from nextcord.ext import commands
from nextcord.ext.menus import Menu
from .api import getuserfromdiscord
import json
import functools
import codecs

with codecs.open(
    "./BOT/lib/bot/config.json", mode="r", encoding="UTF-8"
) as config_file:
    config = json.load(config_file)


# Are you sure?
class AreYouSureView(ui.View):
    def __init__(self, context):
        super().__init__(timeout=None)
        self.context = context
        self.Return = None

    @ui.button(
        label="Yes", custom_id="products:yes_I_am_sure", style=ButtonStyle.success
    )
    async def iamsure(self, _, interaction: Interaction):
        self.Return = True
        self.stop()

    @ui.button(
        label="No", custom_id="products:no_I_am_not_sure", style=ButtonStyle.danger
    )
    async def noiamnotsure(self, _, interaction: Interaction):
        self.Return = False
        self.stop()


# A new send method made to allow reference to be passed but not for interaction responses
async def csend(ctx: Union[commands.Context, Interaction], *args, **kwargs):
    if type(ctx) == Interaction:
        if "reference" in kwargs.keys():
            kwargs.pop("reference")

    return await ctx.send(*args, **kwargs)


async def channelsend(interaction: Interaction, *args, **kwargs):
    if "reference" in kwargs.keys() and interaction.message == None:
        kwargs.pop("reference")

    return await interaction.channel.send(*args, **kwargs)


# A method to get the author of a command no matter if it's a message or an interaction
def getauthor(ctx: Union[commands.Context, Interaction]):
    if type(ctx) == Interaction:
        return ctx.user
    else:
        return ctx.author


def menustart(menu: Menu, ctx: Union[commands.Context, Interaction]):
    if type(ctx) == Interaction:
        return menu.start(interaction=ctx)
    else:
        return menu.start(ctx=ctx)


class UserNotVerified(commands.errors.CheckFailure):
    pass


class UserOwnsProduct(Exception):
    pass


def RequiresVerification():
    def predicate(ctx):
        if getuserfromdiscord(ctx.author.id) is None:
            raise UserNotVerified

        return True

    return commands.check(predicate)
