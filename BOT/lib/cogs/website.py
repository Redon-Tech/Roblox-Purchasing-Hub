"""
    File: /lib/cogs/website.py
    Info: This cog handles the website which talks to the API.
"""
from datetime import datetime
from typing import Union
from nextcord.ext.commands import Cog, command
from nextcord import Embed, Colour
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from ..utils.database import db
from ..utils.api import *
from bson.json_util import ObjectId, dumps
from roblox import Client
from pydantic import BaseModel
import nextcord
import json
import string
import random
import requests
import codecs
import uvicorn

app = FastAPI()

# Get config
with codecs.open(
    "./BOT/lib/bot/config.json", mode="r", encoding="UTF-8"
) as config_file:
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


# This means all requests require authentication, more secure but kinda annoying
@app.middleware("http")
async def is_authorized(request: Request, call_next):
    if request.headers.get("Authorization") == config["api"]["key"]:
        return await call_next(request)

    return JSONResponse(
        status_code=401, content={"error": 401, "details": "API Key is invalid"}
    )


class Tag(BaseModel):
    name: str
    color: list
    textcolor: list


class Product(BaseModel):
    name: str
    description: str
    price: float
    productid: float
    attachments: list
    tags: list
    purchases: Union[float, None]


class Purchase(BaseModel):
    name: str
    description: str
    price: float


@app.get("/")
async def root():
    return {"message": "Online"}


@app.get("/v2/status")
async def status():
    if config["database"]["type"] == "mongodb":
        result = db.command("serverStatus")
        if result:
            return {"message": "Online", "info": {"api": "Ok", "database": "Ok"}}
    elif config["database"]["type"] == "sqlalchemy":
        return {
            "message": "Online",
            "info": {"api": "Ok", "database": "Ok"},
        }  # TODO: Actually check if the database is online

    return {"message": "Online", "info": {"api": "Ok", "database": "Error"}}


@app.get("/v2/products")
async def get_products():
    dbresponse = getproducts()
    results = {}
    for i in dbresponse:
        results[i["name"]] = i
    return results


@app.get("/v2/product/{product}")
async def get_product(product: str):
    dbresponse = getproduct(product)
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/v2/product")
async def create_product(product: Product):
    dbresponse = createproduct(
        product.name,
        product.description,
        product.price,
        product.productid,
        product.attachments,
        product.tags,
        0,
    )
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/v2/product/{product}")
async def delete_product(product: str):
    if not getproduct(product):
        raise HTTPException(status_code=404, detail="Product not found")

    dbresponse = deleteproduct(product)
    if dbresponse:
        return {"message": "Product deleted"}
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/v2/product/{product}")
async def update_product(product: str, product_info: Product):
    if not getproduct(product):
        raise HTTPException(status_code=404, detail="Product not found")

    if not product_info.purchases:
        product_info.purchases = getproduct(product)["purchases"]

    dbresponse = updateproduct(
        product,
        product_info.name,
        product_info.description,
        product_info.price,
        product_info.productid,
        product_info.attachments,
        product_info.tags,
        product_info.purchases,
    )
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/v2/users")
async def get_users():
    dbresponse = getusers()
    results = {}
    for i in dbresponse:
        results[i["_id"]] = i
    return results


@app.get("/v2/user/{user}")
async def get_user(user: str):
    dbresponse = getuser(user)
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/v2/user/{userid}/verify")
async def verify_user(userid: str):
    user = getuser(userid)
    if not user or not user["discordid"]:
        key = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        verificationkeys[key] = userid
        return {"message": "Key generated", "key": key}

    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/v2/user/{user}/product/{product}")
async def add_product_to_user(user: str, product: str):
    if not getuser(user):
        raise HTTPException(status_code=404, detail="User not found")

    try:
        giveproduct(user, product)
        userinfo = getuser(user)
        member = nextcord.utils.get(sbot.users, id=userinfo["discordid"])
        if member != None:  # Try to prevent it from returning an error
            product = getproduct(product)
            productname = product["name"]
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

        return userinfo
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/v2/user/{user}/product/{product}")
async def remove_product_from_user(user: str, product: str):
    if not getuser(user):
        raise HTTPException(status_code=404, detail="User not found")

    try:
        revokeproduct(user, product)
        userinfo = getuser(user)

        return userinfo
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/v2/tags")
async def get_tags():
    dbresponse = gettags()
    results = {}
    for i in dbresponse:
        results[i["name"]] = i
    return results


@app.get("/v2/tag/{tag}")
async def get_tag(tag: str):
    dbresponse = gettag(tag)
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=404, detail="Tag not found")


@app.post("/v2/tag")
async def create_tag(tag: Tag):
    dbresponse = createtag(tag.name, tag.color, tag.textcolor)
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/v2/tag/{tag}")
async def delete_tag(tag: str):
    if not gettag(tag):
        raise HTTPException(status_code=404, detail="Tag not found")

    dbresponse = deletetag(tag)
    if dbresponse:
        return {"message": "Tag deleted"}
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/v2/tag/{tag}")
async def update_tag(tag: str, tag_info: Tag):
    if not gettag(tag):
        raise HTTPException(status_code=404, detail="tag not found")

    dbresponse = updatetag(
        tag,
        tag_info.name,
        tag_info.color,
        tag_info.textcolor,
    )
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/v2/purchases")
async def create_purchase(universeId: int, purchase: Purchase):
    try:
        # We still have to create a purchase for ever purchase instead of reusing old ones
        # Because Roblox is yet to update there API or even document there API on getting developer products
        # I do know we could use more HTML parsing to get the product ID but its unreliable and isnt a API
        # I could also use there sunsetted version but it wont be working in a few days
        # So we are waiting for Roblox to do that
        # And I am def not waisting database space on it
        url = f"https://develop.roblox.com/v1/universes/{universeId}/developerproducts?name={purchase.name}&description={purchase.description}%20creation&priceInRobux={purchase.price}"
        cookies = {".ROBLOSECURITY": config["roblox"]["cookie"]}

        x_csrf_r = requests.post(
            "https://auth.roblox.com/v2/logout",
            data=None,
            cookies=cookies,
        )
        if "x-csrf-token" in x_csrf_r.headers:
            headers = {"x-csrf-token": x_csrf_r.headers["x-csrf-token"]}
            r = requests.post(
                url,
                data=None,
                cookies=cookies,
                headers=headers,
            )
            if r.status_code == 200:
                return r.json()
    except Exception as e:
        raise HttpException(status_code=500, detail="Internal Server Error")


server = uvicorn.Server(
    uvicorn.Config(
        app,
        host=config["api"]["ip"],
        port=config["api"]["port"],
        loop="none",
    )
)

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
                await ctx.author.edit(nick=username)
            except Exception as e:
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
            self.bot.loop.create_task(server.serve())


def setup(bot):
    bot.add_cog(Website(bot))
