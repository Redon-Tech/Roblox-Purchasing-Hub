"""
    File: /lib/utils/database.py
    Useage: Used to do anything to databasses
    Info: The only reason this exists is so if you want to change databases you can.
"""
from pymongo import MongoClient

with open("./BOT/lib/utils/mongopassword", "r", encoding="utf-8") as tf:
    password = tf.read()

client = MongoClient(
    f"mongodb+srv://dbUser:{password}@test-database.fs6p3.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
)
db = client.api

print(db.command("serverStatus"))
