"""
    File: /lib/utils/util.py
    Info: Standard utilility file.
"""

from quart import request
import json
import functools

with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)


def require_apikey(view):
    # Makes it so I dont repeat if apikey in every website base.
    @functools.wraps(view)
    async def wrapper(*args, **kwargs):
        apikey = request.headers["apikey"]
        if not apikey == config["apikey"]:
            return {"errors": [{"message": "Improper API key passed"}]}
        return await view(*args, **kwargs)

    return wrapper
