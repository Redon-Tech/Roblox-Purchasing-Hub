<h1 align="center">Roblox Purchasing Hub</h1>

<div align="center">
  
  [![Discord](https://img.shields.io/discord/536555061510144020?label=discord&logo=discord&style=for-the-badge)](https://discord.gg/Eb384Xw)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
  [![GitHub](https://img.shields.io/github/license/redon-tech/Roblox-Purchasing-Hub?style=for-the-badge)](https://mit-license.org/)
  [![GitHub release (latest by date)](https://img.shields.io/github/v/release/redon-tech/Roblox-Purchasing-Hub?style=for-the-badge)](https://github.com/Redon-Tech/Roblox-Purchasing-Hub/releases)
  [![CodeFactor](https://img.shields.io/codefactor/grade/github/Redon-Tech/Roblox-Purchasing-Hub/development?style=for-the-badge)](https://www.codefactor.io/repository/github/redon-tech/roblox-purchasing-hub/overview/development)
  
</div>

# Work In Progress

This system is still a major work in progress stay tunned for release!

Please ignore everything below for now.

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

## Bot & API

### Requirements
- Get a computer or VPS to host the bot on.
  - Make sure it has a port open for the bot to run on.
  - Note: Glitch will not work for hosting unless you have boosted your project. Replit and Heroku will work as long as you ping it to keep it online.
- Have a database setup on [MongoDB](https://www.mongodb.com/)
- Have a [Discord bot](https://discord.com/developers) setup and the token ready.
- Have a Roblox cookie ready. (Toturial on how to get soon)
- Python 3.9 Installed(With pip)

### Installation
1. Clone this repository into the directory you want it in.
    ```
    Via Git:
    git clone https://github.com/Redon-Tech/Roblox-Purchasing-Hub
    ```
2. Install requirements
    ```
    cd /BOT
    pip3 install requirements.txt
    ```
    If that isnt working do
    ```
    pip install requirements.txt
    ```
3. In BOT/lib/bot clone the config.example.json and rename it to config.json
4. Edit config.json and update it with all the proper information
5. Run the bot by executing BOT/launcher.py
    ```
    python3 launcher.py
    ```
    If that isnt working do
    ```
    python launcher.py
    ```
6. Test that the bot is online by using `{prefix}help`

## Roblox



# Advanced Documentation

[Visit the docs](https://redon-tech.github.io/RPH-Docs/)

# Developer Info

## TD

| Status      | Name              | Description                                                                      |
| ----------- | ----------------- | -------------------------------------------------------------------------------- |
| Complete    | Product API       | Create, delete, update products                                                  |
| Complete    | User API          | Verify, give products, revoke products                                           |
| Complete    | Bot Commands      | Commands to create, delete, update product and verify, give products, and revoke |
| In Progress | Create hub GUI    | A simple UI that does not need to be advanced.                                   |
| Complete    | Developer Product | A system that creates developer products automatically to make a cart system.    |