"""
    File: /lib/cogs/website.py
    Info: This cog handles the website which talks to the API.
"""
from nextcord.ext.commands import Cog, command
from nextcord.ext.commands.core import Command
from quart import Quart, request
from ..utils.database import db
from ..utils.api import *
from bson.json_util import ObjectId, dumps
import json

app = Quart(__name__)

# Had to do this cause I cant pass in self in quart
with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)

# Define Functions

## This needs to be done with the MongoDB database to make sure the _id is a string and not ObjectId
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)


app.json_encoder = MyEncoder

# Website Handling


@app.route("/", methods=["GET"])
async def index():
    return {"message": "Ok"}


@app.route("/v1/status", methods=["GET"])
async def status():
    result = db.command("serverStatus")
    if result:
        return {"message": "Ok", "info": {"api": "Ok", "database": "Ok"}}
    else:
        return {"message": "Ok", "info": {"api": "Ok", "database": "Error"}}


@app.route("/v1/products", methods=["GET"])
async def products():
    dbresponse = getproducts()
    results = {}
    for i in dbresponse:
        results[i["name"]] = i
    return results


@app.route("/v1/create_product", methods=["POST"])
async def create_product():
    apikey = request.headers["apikey"]
    if apikey == config["apikey"]:
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
            return {"errors": [{"msessage": "Unable to delete product"}]}
    # Based off of Roblox API errors
    return {"errors": [{"msessage": "Improper API key passed"}]}


@app.route("/v1/update_product", methods=["POST"])  # broken idk why
async def update_product():
    apikey = request.headers["apikey"]
    if apikey == config["apikey"]:
        info = await request.get_json()
        # try:
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
        # except:
        #    return {"errors": [{"msessage": "Unable to update product"}]}
    # Based off of Roblox API errors
    return {"errors": [{"msessage": "Improper API key passed"}]}


@app.route("/v1/delete_product", methods=["DELETE"])
async def delete_product():
    apikey = request.headers["apikey"]
    if apikey == config["apikey"]:
        info = await request.get_json()
        try:
            deleteproduct(info["name"])
            return {"message": "Deleted"}
        except:
            return {"errors": [{"msessage": "Unable to create product"}]}
    # Based off of Roblox API errors
    return {"errors": [{"msessage": "Improper API key passed"}]}


@app.route("/v1/user", methods=["GET"])
async def get_user():
    info = await request.get_json()
    dbresponse = getuser(info["userid"])
    return dumps(dbresponse)[1:-1]


@app.route("/v1/verify_user", methods=["POST"])
async def verify_user():
    apikey = request.headers["apikey"]
    if apikey == config["apikey"]:
        info = await request.get_json()
        try:
            verifyuser(info["userid"], info["username"])
            userinfo = getuser(info["userid"])
            return dumps(userinfo)[1:-1]
        except:
            return {"errors": [{"msessage": "Unable to create user"}]}
    # Based off of Roblox API errors
    return {"errors": [{"msessage": "Improper API key passed"}]}


@app.route("/v1/give_product", methods=["POST"])
async def give_product():
    apikey = request.headers["apikey"]
    if apikey == config["apikey"]:
        info = await request.get_json()
        try:
            giveproduct(info["userid"], info["productname"])
            userinfo = getuser(info["userid"])
            return dumps(userinfo)[1:-1]
        except:
            return {"errors": [{"msessage": "Unable to give product"}]}
    # Based off of Roblox API errors
    return {"errors": [{"msessage": "Improper API key passed"}]}


@app.route("/v1/revoke_product", methods=["DELETE"])
async def revoke_product():
    apikey = request.headers["apikey"]
    if apikey == config["apikey"]:
        info = await request.get_json()
        try:
            revokeproduct(info["userid"], info["productname"])
            userinfo = getuser(info["userid"])
            return dumps(userinfo)[1:-1]
        except:
            return {"errors": [{"msessage": "Unable to revoke product"}]}
    # Based off of Roblox API errors
    return {"errors": [{"msessage": "Improper API key passed"}]}


# Bot Handling


class Website(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="website",
        aliases=["web", "ws", "websitestatus"],
        description="Displays if the website is online.",
    )
    async def website(self, ctx):
        if ctx.message.author.id in self.bot.owner_ids:
            await ctx.send("🟢 Website Online")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("website")
            await self.bot.stdout.send("`/lib/cogs/website.py` ready")
            print(" /lib/cogs/website.py ready")


def setup(bot):
    bot.loop.create_task(app.run_task("0.0.0.0"))
    bot.add_cog(Website(bot))
