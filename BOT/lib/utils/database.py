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
import certifi

with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)

client = MongoClient(
    config["mongodb"]["url"], tlsCAFile=certifi.where()
)  # Some systems may not require "tlsCAFile"
db = client.data


def insert(data, info):
    col = db[data]
    result = col.insert_one(info)
    return result


def insertmany(data, info):
    col = db[data]
    results = col.insert_many(info)
    return results


def update(data, query, info):
    col = db[data]
    result = col.update_one(query, info)
    return result


def updatemany(data, query, info):
    col = db[data]
    results = col.update_many(query, info)
    return results


def delete(data, query):
    col = db[data]
    result = col.delete_one(query)
    return result


def deletemany(data, query):
    col = db[data]
    results = col.delete_many(query)
    return results


def find(data, query):
    col = db[data]
    results = col.find(query)
    return results


def find_one(data, query):
    col = db[data]
    results = col.find_one(query)
    return results


def findlimit(data, query, limit):
    col = db[data]
    results = col.find(query).limit(limit)
    return results


database = db  # For any other functions not here use this
