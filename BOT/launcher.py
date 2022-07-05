"""
    File: launcher.py
    Usage: Used to launch the bot
    Info: The only reason this exists is so multiplatforms can launch the bot with ease.
"""
from lib.bot import bot

version = "2.0.0-alpha.2"

bot.run(version, False)
