"""
    File: /lib/cogs/website.py
    Info: This cog handles the website which talks to the API.
"""
from datetime import datetime
from typing import Union
from nextcord.ext.commands import Cog, Context
from nextcord import Embed, Colour, Interaction, Forbidden, SlashOption, ui, ButtonStyle
from nextcord.utils import utcnow
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from ..utils import (
    getauthor,
    command,
    db,
    csend,
    getproducts,
    getproduct,
    createproduct,
    updateproduct,
    deleteproduct,
    gettags,
    gettag,
    createtag,
    updatetag,
    deletetag,
    getusers,
    getuser,
    getuserfromdiscord,
    verifyuser,
    unlinkuser,
    giveproduct,
    revokeproduct,
    config,
)
from bson.json_util import ObjectId, dumps, loads
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
X_API_KEY = OAuth2PasswordBearer(config["api"]["key"])
IS_MONGODB = config["database"]["type"] == "mongodb"
roblox = Client()
verificationkeys = {}
sbot = None
# Define Functions

## This needs to be done with the MongoDB database to make sure the _id is a string and not ObjectId
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return str(obj)
        return super(MyEncoder, self).default(obj)


json_encoder = MyEncoder()

# Website Handling


# This means all requests require authentication, more secure but kinda annoying
def api_auth(x_api_key: str = Depends(X_API_KEY)):
    if x_api_key != config["api"]["key"]:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

    return x_api_key


# Schemas


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


# Helpers
def helper(dictionary: dict) -> dict:
    # Don't even ask, it works and that's all we want
    return json.loads(json.dumps(dictionary, default=str))


@app.get("/")
async def root():
    return {"message": "Online"}


@app.get("/v2/status", dependencies=[Depends(api_auth)])
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


@app.get("/v2/products", dependencies=[Depends(api_auth)])
async def get_products():
    dbresponse = getproducts()
    results = {}
    for i in dbresponse:
        results[i["name"]] = helper(i)
    return results


@app.get("/v2/product/{product}", dependencies=[Depends(api_auth)])
async def get_product(product: str):
    dbresponse = helper(getproduct(product))
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/v2/product", dependencies=[Depends(api_auth)])
async def create_product(product: Product):
    dbresponse = helper(
        createproduct(
            product.name,
            product.description,
            product.price,
            product.productid,
            product.attachments,
            product.tags,
            0,
        )
    )
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/v2/product/{product}", dependencies=[Depends(api_auth)])
async def delete_product(product: str):
    if not getproduct(product):
        raise HTTPException(status_code=404, detail="Product not found")

    dbresponse = deleteproduct(product)
    if dbresponse:
        return {"message": "Product deleted"}
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/v2/product/{product}", dependencies=[Depends(api_auth)])
async def update_product(product: str, product_info: Product):
    if not getproduct(product):
        raise HTTPException(status_code=404, detail="Product not found")

    if not product_info.purchases:
        product_info.purchases = getproduct(product)["purchases"]

    dbresponse = helper(
        updateproduct(
            product,
            product_info.name,
            product_info.description,
            product_info.price,
            product_info.productid,
            product_info.attachments,
            product_info.tags,
            product_info.purchases,
        )
    )
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/v2/users")
async def get_users():
    dbresponse = getusers()
    results = {}
    for i in dbresponse:
        results[i["_id"]] = helper(i)
    return results


@app.get("/v2/user/{user}")
async def get_user(user: str):
    dbresponse = helper(getuser(user))
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/v2/user/{userid}/verify", dependencies=[Depends(api_auth)])
async def verify_user(userid: str):
    user = getuser(userid)
    if not user or not user["discordid"]:
        key = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        verificationkeys[key] = userid
        return {"message": "Key generated", "key": key}

    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/v2/user/{user}/product/{product}", dependencies=[Depends(api_auth)])
async def add_product_to_user(user: str, product: str):
    if not getuser(user):
        raise HTTPException(status_code=404, detail="User not found")

    try:
        giveproduct(user, product)
        userinfo = helper(getuser(user))
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


@app.delete("/v2/user/{user}/product/{product}", dependencies=[Depends(api_auth)])
async def remove_product_from_user(user: str, product: str):
    if not getuser(user):
        raise HTTPException(status_code=404, detail="User not found")

    try:
        revokeproduct(user, product)
        userinfo = helper(getuser(user))

        return userinfo
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/v2/tags")
async def get_tags():
    dbresponse = gettags()
    results = {}
    for i in dbresponse:
        results[i["name"]] = helper(i)
    return results


@app.get("/v2/tag/{tag}")
async def get_tag(tag: str):
    dbresponse = helper(gettag(tag))
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=404, detail="Tag not found")


@app.post("/v2/tag", dependencies=[Depends(api_auth)])
async def create_tag(tag: Tag):
    dbresponse = helper(createtag(tag.name, tag.color, tag.textcolor))
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/v2/tag/{tag}", dependencies=[Depends(api_auth)])
async def delete_tag(tag: str):
    if not gettag(tag):
        raise HTTPException(status_code=404, detail="Tag not found")

    dbresponse = deletetag(tag)
    if dbresponse:
        return {"message": "Tag deleted"}
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/v2/tag/{tag}", dependencies=[Depends(api_auth)])
async def update_tag(tag: str, tag_info: Tag):
    if not gettag(tag):
        raise HTTPException(status_code=404, detail="tag not found")

    dbresponse = helper(
        updatetag(
            tag,
            tag_info.name,
            tag_info.color,
            tag_info.textcolor,
        )
    )
    if dbresponse:
        return dbresponse
    raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/v2/purchases", dependencies=[Depends(api_auth)])
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
        raise HTTPException(status_code=500, detail="Internal Server Error")


server = uvicorn.Server(
    uvicorn.Config(
        app,
        host=config["api"]["ip"],
        port=config["api"]["port"],
        loop="none",
    )
)

# Bot Handling


class VerifyButton(ui.Button):
    def __init__(self, label):
        super().__init__(
            label=label,
            style=ButtonStyle.primary,
            disabled=not config["roblox"]["verification"][label.lower()]["enabled"],
        )
        self.label = label

    async def callback(self, interaction: Interaction):
        self.view.Return = self.label.lower()
        self.view.stop()


class VerifyButtons(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.Return = None
        self.bot = bot
        self.add_item(VerifyButton("Bloxlink"))
        self.add_item(VerifyButton("RoVer"))


class Website(Cog):
    def __init__(self, bot):
        global sbot
        sbot = bot
        self.bot = bot

    # @command(
    #     name="website",
    #     aliases=["web", "ws", "websitestatus"],
    #     brief="Displays if the website is online.",
    #     catagory="misc",
    # )
    # async def website(self, ctx):
    #     await ctx.send("🟢 Website Online")

    @command(
        name="verify",
        aliases=["link"],
        brief="Verify's you as a user.",
        catagory="user",
    )
    async def verify(
        self,
        ctx: Union[Context, Interaction],
        key: str = SlashOption(
            name="key",
            description="The key that was provided from the hub",
            required=False,
        ),
    ):
        author = getauthor(ctx)
        if not key:
            embed = Embed(
                title="Verify",
                description="Please choose the source of verification that you want to use.",
                colour=author.colour,
                timestamp=utcnow(),
            )
            embed.set_footer(text="Redon Hub • By: parker02311")
            view = VerifyButtons(bot=self.bot)
            message = await csend(ctx, embed=embed, view=view, reference=ctx.message)
            await view.wait()
            if view.Return == "bloxlink":
                request = requests.get(
                    f"https://v3.blox.link/developer/discord/{author.id}?guildId={self.bot.config['discord']['primaryguild']}",
                    headers={
                        "api-key": self.bot.config["roblox"]["verification"][
                            "bloxlink"
                        ]["key"]
                    },
                )
                if request.status_code == 200:
                    response = request.json()
                    if response["success"] == True:
                        user = await roblox.get_user(response["user"]["robloxId"])
                        username = user.name
                        verifyuser(response["user"]["robloxId"], author.id, username)
                        await message.delete()
                        try:
                            await author.edit(nick=username)
                        except Forbidden:
                            await csend(
                                ctx,
                                "I was unable to change your nickname",
                                delete_after=5.0,
                                reference=ctx.message,
                            )
                        return await csend(
                            ctx,
                            "Verified using Bloxlink",
                            delete_after=5.0,
                            reference=ctx.message,
                        )

                await csend(
                    ctx,
                    "Failed to verify",
                    delete_after=5.0,
                    reference=ctx.message,
                )

            elif view.Return == "rover":
                request = requests.get(
                    f"https://verify.eryn.io/api/user/{author.id}",
                )
                if request.status_code == 200:
                    response = request.json()
                    if response["status"] == "ok":
                        user = await roblox.get_user(response["robloxId"])
                        username = user.name
                        verifyuser(response["robloxId"], author.id, username)
                        await message.delete()
                        try:
                            await author.edit(nick=username)
                        except Forbidden:
                            await csend(
                                ctx,
                                "I was unable to change your nickname",
                                delete_after=5.0,
                                reference=ctx.message,
                            )
                        return await csend(
                            ctx,
                            "Verified using RoVer",
                            delete_after=5.0,
                            reference=ctx.message,
                        )

                await csend(
                    ctx,
                    "Failed to verify",
                    delete_after=5.0,
                    reference=ctx.message,
                )
            else:
                await csend(
                    ctx,
                    "You did not awnser in time or something went wrong please try again.",
                    reference=ctx.message,
                )
                return
        else:
            if key in verificationkeys:
                userid = verificationkeys[key]
                try:
                    user = await roblox.get_user(userid)
                    username = user.name
                    verifyuser(userid, author.id, username)
                    verificationkeys.pop(key)
                    await csend(
                        ctx, "Verified", delete_after=5.0, reference=ctx.message
                    )
                    try:
                        await author.edit(nick=username)
                    except Forbidden:
                        await csend(
                            ctx,
                            "I was unable to change your nickname",
                            delete_after=5.0,
                            reference=ctx.message,
                        )
                except Exception as e:
                    await csend(
                        ctx,
                        "I was unable to verify you",
                        delete_after=5.0,
                        reference=ctx.message,
                    )
            else:
                await csend(
                    ctx,
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
