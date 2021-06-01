"""
    File: /lib/utils/api.py
    Info: This cog defines all the functions for the API.
"""
from .database import db, insert, update, delete, find

## Products
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
        {"$replaceWith": {"name": newname, "description": description, "price": price}},
    )


def deleteproduct(name):
    return delete("products", {"name": name})


## Users
def getuser(userid):
    return find("users", {"_id": userid})


def verifyuser(userid, username):
    return insert("users", {"_id": userid, "username": username, "purchases": []})


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
