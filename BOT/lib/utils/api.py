"""
    File: /lib/utils/api.py
    Info: This cog defines all the functions for the API.
"""
from .database import db, insert, update, delete, find, find_one

## Products
def getproducts():
    return find("products", {})


def getproduct(name):
    return find_one("products", {"name": name})


def createproduct(name, description, price, attachments):
    return insert(
        "products",
        {
            "name": name,
            "description": description,
            "price": price,
            "attachments": attachments,
        },
    )


def updateproduct(oldname, newname, description, price, attachments):
    return update(
        "products",
        {"name": oldname},
        {
            "$set": {
                "name": newname,
                "description": description,
                "price": price,
                "attachments": attachments,
            }
        },
    )


def deleteproduct(name):
    return delete("products", {"name": name})


## Users
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
    purchases = db.users.find_one(
        {"_id": userid}, {"_id": 0, "username": 0, "userid": 0}
    )
    existingpurchases = purchases["purchases"]
    existingpurchases.append(productname)
    return update("users", {"_id": userid}, {"$set": {"purchases": existingpurchases}})


def revokeproduct(userid, productname):
    purchases = db.users.find_one(
        {"_id": userid}, {"_id": 0, "username": 0, "userid": 0}
    )
    existingpurchases = purchases["purchases"]
    existingpurchases.remove(productname)
    return update("users", {"_id": userid}, {"$set": {"purchases": existingpurchases}})
