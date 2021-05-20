"""
    File: /lib/utils/database.py
    Usage: Used to do anything to databasses
    Info: The only reason this exists is so if you want to change databases you can.
    Note: MongoDB is diffrent then most other databases so make sure to update everythin in here and in the cogs.
    Documentation: MongoDB: https://pymongo.readthedocs.io/en/stable/index.html / https://www.w3schools.com/python/python_mongodb_getstarted.asp
"""
from pymongo import MongoClient
from pprint import pprint
import json

with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)

client = MongoClient(config["mongodb"]["url"])
db = client.data


def insert(data, info):
    result = db.data.insert_one(info)
    return result


def insertmany(data, info):
    results = db.data.insert_many(info)
    return results


def update(data, query, info):
    result = db.data.update_one(query, info)
    return result


def updatemany(data, query, info):
    results = db.data.update_many(query, info)
    return results


def delete(data, query):
    result = db.data.delete_one(query)
    return result


def deletemany(data, query):
    results = db.data.delete_many(query)
    return results


def find(data, query):
    results = db.data.find(query)
    return results


def findlimit(data, query, limit):
    results = db.data.find(query).limit(limit)
    return results


database = db  # For any other functions not here use this
