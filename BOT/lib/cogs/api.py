"""
    File: /lib/cogs/api.py
    Info: This cog runs the API alongside some bot stuff so thats pretty cool.
"""
from discord.ext.commands import Cog
from discord import Embed, Colour
from quart import Quart, request
from quart.sessions import NullSession
from ..utils.database import db, insert, update, delete, find
from bson.json_util import ObjectId
import json

app = Quart(__name__)

# Had to do this cause I cant pass in self in quart
with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)

# Define Functions

# This needs to be done with the MongoDB database to make sure the _id is a string and not ObjectId
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)


app.json_encoder = MyEncoder


def getproducts():
    return find("products", {})


def createproduct(name, description, price):
    return insert(
        "products", {"name": name, "description": description, "price": price}
    )


def updateproduct(oldname, newname, description, price):
    return update(
        "products",
        {"name": oldname},
        {"$inc": {"name": newname, "description": description, "price": price}},
    )


def deleteproduct(name):
    return delete("products", {"name": name})


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
            return {"errors": [{"msessage": "Unable to update product"}]}
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


# Bot Handling


class Api(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("api")
            await self.bot.stdout.send("`/lib/cogs/api.py` ready")
            print(" /lib/cogs/api.py ready")


def setup(bot):
    bot.loop.create_task(app.run_task("0.0.0.0"))
    bot.add_cog(Api(bot))
