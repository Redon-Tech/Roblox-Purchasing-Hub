"""
    File: /lib/cogs/help.py
    Info: 
"""
import nextcord
from nextcord.ext.commands import Cog, command
from nextcord.ext.menus import (
    MenuPagesBase,
    ButtonMenu,
    ListPageSource,
    MenuPaginationButton,
    PageSource,
)
from nextcord.utils import get
from nextcord import Embed, Colour, ui, Interaction, SelectOption
from typing import Optional, List
from datetime import datetime


def syntax(command):
    cmd_and_aliases = " | ".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"```{cmd_and_aliases} {params}```"


# Had to redifine it due to some checking issues but is a copy of the official one otherwise
class ButtonMenuPages(MenuPagesBase, ButtonMenu):
    def __init__(
        self,
        source: PageSource,
        style: nextcord.ButtonStyle = nextcord.ButtonStyle.secondary,
        **kwargs,
    ):
        self.__button_menu_pages__ = True
        kwargs["disable_buttons_after"] = kwargs.get("disable_buttons_after", True)
        super().__init__(source, **kwargs)
        if not self.__inherit_buttons__:
            return
        for emoji in (
            self.FIRST_PAGE,
            self.PREVIOUS_PAGE,
            self.NEXT_PAGE,
            self.LAST_PAGE,
            self.STOP,
        ):
            if (
                emoji in {self.FIRST_PAGE, self.LAST_PAGE}
                and self._skip_double_triangle_buttons()
            ):
                continue
            self.add_item(MenuPaginationButton(emoji=emoji, style=style))
        self._disable_unavailable_buttons()

    def _disable_unavailable_buttons(self):
        buttons: List[MenuPaginationButton] = self.children
        max_pages = self._source.get_max_pages()
        for button in buttons:
            if not button.custom_id == "help:select_catagory":
                if button.emoji.name in (self.FIRST_PAGE, self.PREVIOUS_PAGE):
                    button.disabled = self.current_page == 0
                elif max_pages and button.emoji.name in (
                    self.LAST_PAGE,
                    self.NEXT_PAGE,
                ):
                    button.disabled = self.current_page == max_pages - 1


class HelpSelect(ui.Select):
    def __init__(self, context, commands, loadedcommands):
        self.context = context
        self.commands = commands
        self.usercommands = []
        self.productcommands = []
        self.othercommands = []
        for command in commands:
            if command.cog.qualified_name == "User" or command.name == "verify":
                self.usercommands.append(command)
            elif command.cog.qualified_name == "Product":
                self.productcommands.append(command)
            else:
                self.othercommands.append(command)
        placeholder = ""
        if loadedcommands == self.usercommands:
            placeholder = "User"
        elif loadedcommands == self.productcommands:
            placeholder = "Product"
        elif loadedcommands == self.othercommands:
            placeholder = "Misc"
        else:
            placeholder = "All"
        super().__init__(
            custom_id="help:select_catagory",
            options=[
                SelectOption(label="All", description="View help on all commands."),
                SelectOption(
                    label="User", description="View help on all user commands."
                ),
                SelectOption(
                    label="Product", description="View help on all product commands."
                ),
                SelectOption(
                    label="Misc", description="View help on all other commands."
                ),
            ],
            row=1,
            placeholder=placeholder,
        )

    async def callback(self, interaction: Interaction):
        selection = str(interaction.data["values"])[2:-2]

        if selection:
            if selection == "All":
                menu = ButtonMenuPages(
                    source=HelpMenu(self.context, self.commands, self.commands),
                    clear_reactions_after=True,
                    timeout=60.0,
                    style=nextcord.ButtonStyle.primary,
                )
                await menu.start(self.context)
                await interaction.message.delete()
            elif selection == "User":
                menu = ButtonMenuPages(
                    source=HelpMenu(self.context, self.commands, self.usercommands),
                    clear_reactions_after=True,
                    timeout=60.0,
                    style=nextcord.ButtonStyle.primary,
                )
                await menu.start(self.context)
                await interaction.message.delete()
            elif selection == "Product":
                menu = ButtonMenuPages(
                    source=HelpMenu(self.context, self.commands, self.productcommands),
                    clear_reactions_after=True,
                    timeout=60.0,
                    style=nextcord.ButtonStyle.primary,
                )
                await menu.start(self.context)
                await interaction.message.delete()
            elif selection == "Misc":
                menu = ButtonMenuPages(
                    source=HelpMenu(self.context, self.commands, self.othercommands),
                    clear_reactions_after=True,
                    timeout=60.0,
                    style=nextcord.ButtonStyle.primary,
                )
                await menu.start(self.context)
                await interaction.message.delete()


class HelpMenu(ListPageSource):
    def __init__(self, ctx, commands, data):
        self.ctx = ctx
        self.commands = commands

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

    async def format_page(self, menu: ButtonMenuPages, entries):
        fields = []

        for entry in entries:
            fields.append((entry.brief or "No description", syntax(entry)))

        menu.clear_items()
        menu.add_item(
            MenuPaginationButton(
                emoji=menu.PREVIOUS_PAGE, style=nextcord.ButtonStyle.primary
            )
        )
        menu.add_item(
            MenuPaginationButton(
                emoji=menu.NEXT_PAGE, style=nextcord.ButtonStyle.primary
            )
        )
        menu.add_item(
            MenuPaginationButton(emoji=menu.STOP, style=nextcord.ButtonStyle.primary)
        )

        menu.add_item(HelpSelect(self.ctx, self.commands, entries))

        menu._disable_unavailable_buttons()

        return {"embed": await self.write_page(menu, fields), "view": menu}


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
        await ctx.send(embed=embed, reference=ctx.message)

    @command(name="help", brief="Shows this message", catagory="misc")
    async def show_help(self, ctx, cmd: Optional[str]):
        if cmd is None:
            menu = ButtonMenuPages(
                source=HelpMenu(ctx, list(self.bot.commands), list(self.bot.commands)),
                clear_reactions_after=True,
                timeout=60.0,
                style=nextcord.ButtonStyle.primary,
            )
            await menu.start(ctx)

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
