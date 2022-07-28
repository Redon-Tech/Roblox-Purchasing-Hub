"""
    File: /lib/utils/api.py
    Info: This cog defines all the functions for the API.
"""
from .database import db, insert, update, delete, find, find_one
import datetime

## Products
def getproducts():
    return find("products", {})


def getproduct(name):
    return find_one("products", {"name": name})


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
    purchases = find_one("users", {"_id": userid})
    existingpurchases = purchases["purchases"]
    existingpurchases.append(productname)
    return update("users", {"_id": userid}, {"$set": {"purchases": existingpurchases}})


def revokeproduct(userid, productname):
    purchases = find_one("users", {"_id": userid})
    existingpurchases = purchases["purchases"]
    existingpurchases.remove(productname)
    return update("users", {"_id": userid}, {"$set": {"purchases": existingpurchases}})
