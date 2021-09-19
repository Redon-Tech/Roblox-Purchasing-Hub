"""
    File: /lib/cogs/help.py
    Info: 
"""
import nextcord
from nextcord.ext.commands import Cog, command
from nextcord.ext.menus import ButtonMenuPages, ListPageSource
from nextcord.utils import get
from nextcord import Embed, Colour, ui, Interaction, SelectOption
from typing import Optional
from datetime import datetime


def syntax(command):
    cmd_and_aliases = " | ".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"```{cmd_and_aliases} {params}```"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=5)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
            title="Help",
            description="Get help on all commands!",
            colour=self.ctx.author.colour,
            timestamp=nextcord.utils.utcnow(),
        )
        embed.set_footer(
            text=f"Redon Tech RPH • {offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands • By: parker02311"
        )

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []

        for entry in entries:
            fields.append((entry.brief or "No description", syntax(entry)))

        return await self.write_page(menu, fields)


class HelpSelect(ui.View):
    def __init__(self, context, commands, *, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.context = context
        self.commands = commands

    @ui.select(
        custom_id="help:select_catagory",
        options=[
            SelectOption(label="All", description="View help on all commands."),
            SelectOption(label="User", description="View help on all user commands."),
            SelectOption(
                label="Product", description="View help on all product commands."
            ),
            SelectOption(label="Misc", description="View help on all other commands."),
        ],
    )
    async def select_catagory(self, _, interaction: Interaction):
        selection = str(interaction.data["values"])[2:-2]
        usercommands = []
        productcommands = []
        othercommands = []
        for command in self.commands:
            if command.cog.qualified_name == "User" or command.name == "verify":
                usercommands.append(command)
            elif command.cog.qualified_name == "Product":
                productcommands.append(command)
            else:
                othercommands.append(command)

        if selection:
            if selection == "All":
                menu = ButtonMenuPages(
                    source=HelpMenu(self.context, self.commands),
                    clear_reactions_after=True,
                    timeout=60.0,
                    style=nextcord.ButtonStyle.primary,
                )
                await menu.start(self.context)
                await interaction.message.delete()
            elif selection == "User":
                menu = ButtonMenuPages(
                    source=HelpMenu(self.context, usercommands),
                    clear_reactions_after=True,
                    timeout=60.0,
                    style=nextcord.ButtonStyle.primary,
                )
                await menu.start(self.context)
                await interaction.message.delete()
            elif selection == "Product":
                menu = ButtonMenuPages(
                    source=HelpMenu(self.context, productcommands),
                    clear_reactions_after=True,
                    timeout=60.0,
                    style=nextcord.ButtonStyle.primary,
                )
                await menu.start(self.context)
                await interaction.message.delete()
            elif selection == "Misc":
                menu = ButtonMenuPages(
                    source=HelpMenu(self.context, othercommands),
                    clear_reactions_after=True,
                    timeout=60.0,
                    style=nextcord.ButtonStyle.primary,
                )
                await menu.start(self.context)
                await interaction.message.delete()


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        embed = Embed(
            title=f"Help with `{command}`",
            description=syntax(command),
            colour=ctx.author.colour,
        )
        embed.add_field(name="Command Description", value=command.brief)
        embed.set_footer(text="Pembroke Bot • By: parker02311")
        await ctx.send(embed=embed)

    @command(name="help", brief="Shows this message", catagory="misc")
    async def show_help(self, ctx, cmd: Optional[str]):
        if cmd is None:
            embed = Embed(
                title="Help",
                description="Get help on commands!",
                colour=ctx.author.colour,
                timestamp=nextcord.utils.utcnow(),
            )
            await ctx.send(
                embed=embed, view=HelpSelect(ctx, commands=list(self.bot.commands))
            )

        else:
            if command := get(self.bot.commands, name=cmd):
                await self.cmd_help(ctx, command)

            else:
                for command in self.bot.commands:
                    if cmd in command.aliases:
                        await self.cmd_help(ctx, command)
                        return

                await ctx.send("That command doesnt exist.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("help")
            await self.bot.stdout.send("`/lib/cogs/help.py` ready")
            print(" /lib/cogs/help.py ready")


def setup(bot):
    bot.add_cog(Help(bot))
