"""
    File: /lib/utils/util.py
    Info: Standard utilility file.
"""

from quart import request
from nextcord import ui, Interaction, SelectOption, ButtonStyle
import json
import functools

with open("./BOT/lib/bot/config.json") as config_file:
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

def require_apikey(view):
    # Makes it so I dont repeat if apikey in every website base.
    @functools.wraps(view)
    async def wrapper(*args, **kwargs):
        apikey = request.headers["apikey"]
        if not apikey == config["apikey"]:
            return {"errors": [{"message": "Improper API key passed"}]}
        return await view(*args, **kwargs)

    return wrapper
