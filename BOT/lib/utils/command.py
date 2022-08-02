"""
    File: /lib/utils/command.py
    Info: Handle implementation of a commands that support both slash and message commands.
"""

from nextcord.ext.commands import Command as CommandBase
from nextcord.ext.commands.core import CommandT
from nextcord.utils import MISSING
from nextcord import SlashApplicationCommand, BaseApplicationCommand
from typing import Type
import codecs
import json
import functools

with codecs.open(
    "./BOT/lib/bot/config.json", mode="r", encoding="UTF-8"
) as config_file:
    config = json.load(config_file)


def command(name: str = MISSING, cls: Type[CommandT] = MISSING, **kwargs):
    if (
        config["discord"]["commands"]["slash_commands"]
        and kwargs.get("no_slash", False) == False
    ):

        def decorator(func) -> SlashApplicationCommand:
            if isinstance(func, BaseApplicationCommand):
                raise TypeError("Callback is already an application command.")

            app_cmd = SlashApplicationCommand(
                callback=func,
                name=name,
                description=kwargs.get("brief"),
                guild_ids=config["discord"]["commands"]["command_guilds"],
                name_localizations=kwargs.get("name_localizations"),
                description_localizations=kwargs.get("description_localizations"),
                dm_permission=kwargs.get("dm_permission"),
                default_member_permissions=kwargs.get("default_member_permissions"),
                force_global=False,
            )
            return app_cmd

        return decorator
    else:
        if cls is MISSING:
            cls = CommandBase

        def decorator(func) -> CommandT:
            if isinstance(func, CommandBase):
                raise TypeError("Callback is already a command.")
            acceptable = {"brief", "aliases", "catagory"}
            kargs = {}
            for k, v in kwargs.items():
                if k in acceptable:
                    kargs[k] = v

            return cls(
                func,
                name=name,
                **kargs,
            )

        return decorator
