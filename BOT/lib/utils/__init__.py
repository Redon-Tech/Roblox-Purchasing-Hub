"""
    File: /lib/utils/__init__.py
    Usage: Used to make all utils import properly.
"""
import codecs
import json

with codecs.open(
    "./BOT/lib/bot/config.json", mode="r", encoding="UTF-8"
) as config_file:
    config = json.load(config_file)

from .api import *
from .command import *
from .database import *
from .util import *
