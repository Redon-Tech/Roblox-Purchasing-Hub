"""
    File: /lib/utils/util.py
    Info: Standard utilility file.
"""

from quart import request
import json

with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)

def require_apikey(view):
    # Makes it so I dont repeat if apikey in every website base.
    @function.wraps(view)
    def wrapper(*args, **kwargs):
        apikey = request.headers["apikey"]
        if apikey == config["apikey"]:
            return view(*args, **kwargs)
        return {"errors": [{"message": "Improper API key passed"}]}