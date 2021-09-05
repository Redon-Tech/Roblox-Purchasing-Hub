"""
    File: launcher.py
    Usage: Used to launch the bot
    Info: The only reason this exists is so multiplatforms can launch the bot with ease.
"""
from lib.bot import bot

version = "0.1"

bot.run(version, False)
