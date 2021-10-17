"""
    File: test.py
    Usage: Used to launch the bot and then close it if it launches
    Info: This is done to allow to test to see if everything is working if not it will fail CircleCI.
"""
from lib.bot import bot

version = "Test deploy"

bot.run(version, True)
