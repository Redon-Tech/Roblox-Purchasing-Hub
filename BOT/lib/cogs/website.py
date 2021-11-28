"""
    File: /lib/cogs/website.py
    Info: This cog handles the website which talks to the API.
"""
from datetime import datetime
from math import prod
import nextcord
from nextcord.ext.commands import Cog, command
from nextcord.ext.commands.core import Command
from nextcord import Embed, Colour, colour
from quart import Quart, request
from ..utils.database import db
from ..utils.api import *
from ..utils.util import require_apikey
from bson.json_util import ObjectId, dumps
from ro_py import Client
from bs4 import BeautifulSoup
import json
import string
import random
import requests
import re

app = Quart(__name__)

# Had to do this cause I cant pass in self in quart
with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)
roblox = Client()
verificationkeys = {}
sbot = None
# Define Functions

## This needs to be done with the MongoDB database to make sure the _id is a string and not ObjectId
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)


app.json_encoder = MyEncoder

# Website Handling


@app.errorhandler(400)
async def error400(error):
    return {"errors": [{"code": 400, "message": "Unable to read that request"}]}


@app.errorhandler(401)
async def error401(error):
    return {
        "errors": [{"code": 401, "message": "You are not allowed to go to that URI"}]
    }


@app.errorhandler(404)
async def error404(error):
    return {"errors": [{"code": 404, "message": "Unable to find that URI"}]}


@app.errorhandler(500)
async def error500(error):
    return {"errors": [{"code": 500, "message": "Something went wrong"}]}


@app.route("/", methods=["GET"])
async def index():
    return {"message": "Ok"}


@app.route("/v1/status", methods=["GET"])
async def status():
    result = db.command("serverStatus")
    if result:
        return {"message": "Ok", "info": {"api": "Ok", "database": "Ok"}}

    return {"message": "Ok", "info": {"api": "Ok", "database": "Error"}}


@app.route("/v1/products", methods=["GET"])
@require_apikey
async def products():
    dbresponse = getproducts()
    results = {}
    for i in dbresponse:
        results[i["name"]] = i
    return results


@app.route("/v1/create_product", methods=["POST"])
@require_apikey
async def create_product():
    info = await request.get_json()
    try:
        createproduct(info["name"], info["description"], info["price"])
        return {
            "info": {
                "name": info["name"],
                "description": info["description"],
                "price": info["price"],
            }
        }
    except:
        return {"errors": [{"message": "Unable to delete product"}]}


@app.route("/v1/update_product", methods=["POST"])
@require_apikey
async def update_product():
    info = await request.get_json()
    try:
        updateproduct(
            info["oldname"], info["newname"], info["description"], info["price"]
        )
        return {
            "info": {
                "name": info["newname"],
                "description": info["description"],
                "price": info["price"],
            }
        }
    except:
        return {"errors": [{"message": "Unable to update product"}]}


@app.route("/v1/delete_product", methods=["DELETE"])
@require_apikey
async def delete_product():
    info = await request.get_json()
    try:
        deleteproduct(info["name"])
        return {"message": "Deleted"}
    except:
        return {"errors": [{"message": "Unable to create product"}]}


# Roblox go brr and I cant use args for whatever stupid reason
@app.route("/v1/user", methods=["GET", "POST"])
async def get_user():
    try:
        info = await request.get_json()
        dbresponse = getuser(info["userid"])
        if dbresponse == None:
            return {"errors": [{"message": "Unable to get user"}]}
        return dumps(dbresponse)
    except:
        return {"errors": [{"message": "Something went wrong when getting user"}]}


@app.route("/v1/verify_user", methods=["POST"])
@require_apikey
async def verify_user():
    info = await request.get_json()
    user = getuser(info["userid"])
    if not user or not user["discordid"]:
        key = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        verificationkeys[key] = info["userid"]
        return {"key": key}

    return {"errors": [{"message": "User is already verified"}]}


@app.route("/v1/give_product", methods=["POST"])
@require_apikey
async def give_product():
    info = await request.get_json()
    try:
        giveproduct(info["userid"], info["productname"])
        userinfo = getuser(info["userid"])
        member = nextcord.utils.get(sbot.users, id=userinfo["discordid"])
        if member != None:  # Try to prevent it from returning an error
            product = getproduct(info["productname"])
            productname = info["productname"]
            if product != None:
                embed = Embed(
                    title="Thanks for your purchase!",
                    description=f"Thank you for your purchase of **{productname}** please get it by using the links below.",
                    colour=Colour.from_rgb(255, 255, 255),
                    timestamp=nextcord.utils.utcnow(),
                )

                await member.send(embed=embed)

                if product["attachments"] != None or product["attachments"] != []:
                    for attachment in product["attachments"]:
                        await member.send(attachment)

        return dumps(userinfo)
    except:
        return {"errors": [{"message": "Unable to give product"}]}


@app.route("/v1/revoke_product", methods=["DELETE"])
@require_apikey
async def revoke_product():
    info = await request.get_json()
    try:
        revokeproduct(info["userid"], info["productname"])
        userinfo = getuser(info["userid"])
        return dumps(userinfo)
    except:
        return {"errors": [{"message": "Unable to revoke product"}]}


@app.route("/v1/create_purchase", methods=["POST"])
@require_apikey
async def create_purchase():
    info = await request.get_json()
    if info["gameid"] and info["name"] and info["price"]:
        data = {
            "universeId": info["gameid"],
            "name": info["name"],
            "priceInRobux": info["price"],
            "description": info["name"] + " " + str(info["price"]),
        }
        cookies = {".ROBLOSECURITY": config["roblox"]["cookie"]}
        # Get the x-csrf-token, this won't actually log you out because there is no x-csrf-token yet.
        # Basically just exploiting the api to give us a x-csrf-token to use.
        r1 = requests.post(
            "https://auth.roblox.com/v2/logout",
            data=None,
            cookies=cookies,
        )
        if r1.headers["x-csrf-token"]:
            headers = {"x-csrf-token": r1.headers["x-csrf-token"]}
            r = requests.post(
                "https://www.roblox.com/places/developerproducts/add",
                data=data,
                cookies=cookies,
                headers=headers,
            )

            if r.status_code == 200:
                return {
                    "ProductId": "".join(
                        re.findall(
                            r"\d",
                            str(
                                BeautifulSoup(r.text, "html.parser").find(
                                    id="DeveloperProductStatus"
                                )
                            ),
                        )
                    )
                }

    return {"errors": [{"message": "Unable to create developer product"}]}


# Bot Handling


class Website(Cog):
    def __init__(self, bot):
        global sbot
        sbot = bot
        self.bot = bot

    @command(
        name="website",
        aliases=["web", "ws", "websitestatus"],
        brief="Displays if the website is online.",
        catagory="misc",
    )
    async def website(self, ctx):
        if ctx.message.author.id in self.bot.owner_ids:
            await ctx.send("🟢 Website Online")

    @command(
        name="verify",
        aliases=["link"],
        brief="Verify's you as a user.",
        catagory="user",
    )
    async def verify(self, ctx, key):
        if key in verificationkeys:
            userid = verificationkeys[key]
            try:
                user = await roblox.get_user(userid)
                username = user.name
                verifyuser(userid, ctx.author.id, username)
                verificationkeys.pop(key)
                await ctx.send("Verified", delete_after=5.0, reference=ctx.message)
            except:
                await ctx.send(
                    "I was unable to verify you",
                    delete_after=5.0,
                    reference=ctx.message,
                )
        else:
            await ctx.send(
                "The provided key was incorrect please check the key and try again.",
                delete_after=5.0,
                reference=ctx.message,
            )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("website")
            await self.bot.stdout.send("`/lib/cogs/website.py` ready")
            print(" /lib/cogs/website.py ready")


def setup(bot):
    bot.loop.create_task(
        app.run_task("0.0.0.0")
    )  # It is highly recomended that you change "0.0.0.0" to your server IP in a production env
    bot.add_cog(Website(bot))
