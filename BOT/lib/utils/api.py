"""
    File: /lib/utils/api.py
    Info: This cog defines all the functions for the API.
"""
from .database import db, insert, update, delete, find, find_one
from typing import Union
import datetime

## Products
def getproducts() -> dict:
    return find("products", {})


def getproduct(query: Union[str, int]) -> Union[dict, None]:
    try:
        return find_one("products", {"name": query}) or find_one(
            "products", {"_id": query}
        )
    except Exception as e:
        return None


def createproduct(name, description, price, productid, attachments, tags, purchases):
    return insert(
        "products",
        {
            "name": name,
            "description": description,
            "price": price,
            "productid": productid,
            "attachments": attachments,
            "purchases": purchases,
            "tags": tags,
            "created": datetime.datetime.now(),
        },
    )


def updateproduct(
    oldname, newname, description, price, productid, attachments, tags, purchases
):
    return update(
        "products",
        {"name": oldname},
        {
            "$set": {
                "name": newname,
                "description": description,
                "price": price,
                "productid": productid,
                "attachments": attachments,
                "tags": tags,
                "purchases": purchases,
            }
        },
    )


def deleteproduct(name):
    return delete("products", {"name": name})


## Tags
def gettags():
    return find("tags", {})


def gettag(name):
    return find_one("tags", {"name": name})


def createtag(name, color, textcolor):
    return insert(
        "tags",
        {"name": name, "color": color, "textcolor": textcolor},
    )


def updatetag(oldname, newname, color, textcolor):
    return update(
        "tags",
        {"name": oldname},
        {"$set": {"name": newname, "color": color, "textcolor": textcolor}},
    )


def deletetag(name):
    return delete("tags", {"name": name})


## Users
def getusers():
    return find("users", {})


def getuser(userid):
    return find_one("users", {"_id": userid})


def getuserfromdiscord(discordid):
    return find_one("users", {"discordid": discordid})


def verifyuser(userid, discordid, username):
    if getuser(userid) is None:
        return insert(
            "users",
            {
                "_id": userid,
                "discordid": discordid,
                "username": username,
                "purchases": [],
            },
        )

    return update("users", {"_id": userid}, {"$set": {"discordid": discordid}})


def unlinkuser(userid):
    return update("users", {"_id": userid}, {"$set": {"discordid": None}})


def giveproduct(userid, productname):
    product = getproduct(productname)
    purchases = find_one("users", {"_id": userid})
    existingpurchases = list(dict.fromkeys(purchases["purchases"]))
    existingpurchases.append(product["_id"])
    return update("users", {"_id": userid}, {"$set": {"purchases": existingpurchases}})


def revokeproduct(userid, productname):
    purchases = find_one("users", {"_id": userid})
    existingpurchases = list(dict.fromkeys(purchases["purchases"]))
    actualproduct = getproduct(productname)
    if actualproduct["name"] in existingpurchases:
        existingpurchases.remove(actualproduct["name"])
    if actualproduct["_id"] in existingpurchases:
        existingpurchases.remove(actualproduct["_id"])
    return update("users", {"_id": userid}, {"$set": {"purchases": existingpurchases}})
