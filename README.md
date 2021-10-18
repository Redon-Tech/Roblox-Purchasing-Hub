<h1 align="center">Roblox Purchasing Hub</h1>

<div align="center">
  
  [![Discord](https://img.shields.io/discord/536555061510144020?label=discord&logo=discord&style=for-the-badge)](https://discord.gg/Eb384Xw)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
  [![GitHub](https://img.shields.io/github/license/redon-tech/Roblox-Purchasing-Hub?style=for-the-badge)](https://mit-license.org/)
  [![Latest Release](https://img.shields.io/github/v/release/redon-tech/Roblox-Purchasing-Hub?style=for-the-badge)](https://github.com/Redon-Tech/Roblox-Purchasing-Hub/releases)
  [![CodeFactor](https://img.shields.io/codefactor/grade/github/Redon-Tech/Roblox-Purchasing-Hub?style=for-the-badge)](https://www.codefactor.io/repository/github/redon-tech/roblox-purchasing-hub/overview)
  
</div>

# Table of Contents

Go to the top left and hit the list button to see the table of contents!

# Overview

This system is designed to be self-hosted if you want a hosted option visit [Redon Tech RPH](https://rph.redon.tech)(WIP).
This purchasing system is designed to be just a great as other systems such as myPod, Kireko, ect. with more features and 100% free and open source.

## Features

- Product Purchasing (Cart System)

## Planed Features

- Product Whitelist
- Product Transfer
- Product Loaning
- Product Testing
- Product Licensing
- Monthly Subscriptions (Via Private Servers and dev products)

If you have any suggestions join the Discord and let us know!

# Installation

[Video](https://youtu.be/0eVR3i_ZKoQ)

## Bot & API

### Requirements
- Get a computer or VPS to host the bot on.
  - Make sure it has a port open for the bot to run on.
  - Note: Glitch will not work for hosting unless you have boosted your project. Replit and Heroku will work as long as you ping it to keep it online.
- Have a database setup on [MongoDB](https://www.mongodb.com/)
- Have a [Discord bot](https://discord.com/developers) setup and the token ready.
- Have a Roblox cookie ready. (Toturial on how to get soon)
- Python 3.9 Installed(With pip)
- Git installed for fast setup

### Installation
1. Clone this repository into the directory you want it in.
    
    Via Git:
    ```
    git clone https://github.com/Redon-Tech/Roblox-Purchasing-Hub
    ```
    Via Get(Development Version):
    ```
    git clone -b development https://github.com/Redon-Tech/Roblox-Purchasing-Hub
    ```
2. Install requirements
    ```
    cd Roblox-Purchasing-Hub

    pip3 install -r BOT/requirements.txt
    ```
    If that isnt working do
    ```
    pip install -r BOT/requirements.txt
    ```
3. In BOT/lib/bot clone the example.config.json and rename it to config.json
4. Edit config.json and update it with all the proper information (Guide on configuration below)
5. Run the bot by executing BOT/launcher.py
    ```
    python3 BOT/launcher.py
    ```
    If that isnt working do
    ```
    python BOT/launcher.py
    ```
6. Test that the bot is online by using `{prefix}help` (Default Prefix: ".")

### Configuration
```json
{
    "token": "",
    "prefix": ".",
    "ownerids": [
        1234567890
    ],
    "guild": 1234567890,
    "standardoutput": 123467890,
    "usepages": true,
    "mongodb": {
        "url": "mongodburl"
    },
    "roblox": {
        "cookie": "fullrobloxcookie"
    },
    "apikey": "generatearandomstringforthis"
}
```

- Token [String]: The token of your bot found at [Discord Developer Portal](https://discord.com/developers).
- Prefix [String]: The prefix of the bot. [Default: "."]
- OwnerIds [List of Numbers]: List of all the bot owners, used for owner commands.
- Guild: [Number]: The primary guild id of the bot. Also the guild that the standard output channel is in.
- StandardOutpu [Number]: The output channel id for bot logs.
- UsePages [Bool]: N/A
- MongoDB [Dictionary]: All information for MongoDB
- MongoDB.URL [String]: The connection URL to your [MongoDB](https://www.mongodb.com/) server.
- Roblox [Dictionary]: All information for Roblox
- Roblox.Cookie [String]: The full Roblox cookie of your Roblox bot.
- ApiKey [String]: Should be a random string used for communication between API and database.

## Roblox

## Fast Installation
For creating a new place.
1. Download the RBXL file from the [latest release full](https://github.com/Redon-Tech/Roblox-Purchasing-Hub/releases).
2. Open the file.
3. In ServerScriptService open Server/Handler.
4. Change `local Server = "http://143.198.139.168:25503"` to `local Server = "yourserveradresshere"` makes sure there is no trailing slash.
5. Change ApiKey to the ApiKey you set in config.json.
6. Change PlaceId to the a PlaceId of which your Roblox bot can create developer products on.
7. Publish and make sure HttpRequests is on.

## Manual Installation

1. Download the RBXM file from the [latest release full](https://github.com/Redon-Tech/Roblox-Purchasing-Hub/releases).
2. Put it into your place
3. Move Client to StarterPlayer/StarterPlayerScripts.
4. Move Common to ReplicatedStorage
5. Move Server to ServerScriptService
6. Delete README.MD
7. Move GUI to StarterGui
8. In ServerScriptService open Server/Handler.
9. Change `local Server = "http://143.198.139.168:25503"` to `local Server = "yourserveradresshere"` makes sure there is no trailing slash.
10. Change ApiKey to the ApiKey you set in config.json.
11. Change PlaceId to the a PlaceId of which your Roblox bot can create developer products on.
12. Publish and make sure HttpRequests is on.

# Advanced Documentation

[Visit the docs](https://redon-tech.github.io/RPH-Docs/)

# Developer Info

## TD

### V1.0

| Status   | Name              | Description                                                                      |
| -------- | ----------------- | -------------------------------------------------------------------------------- |
| Complete | Product API       | Create, delete, update products                                                  |
| Complete | User API          | Verify, give products, revoke products                                           |
| Complete | Bot Commands      | Commands to create, delete, update product and verify, give products, and revoke |
| Complete | Create hub GUI    | A simple UI that does not need to be advanced.                                   |
| Complete | Developer Product | A system that creates developer products automatically to make a cart system.    |
