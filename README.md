# PSBot
 Multi-functional Discord bot aimed at PlayStation Gamers.
 
 Written in Python 3.7.1 using Discord's latest bot API.

## Features
* Searches for trophy lists, game sales, scores and lengths utilizing Google Search for maximum accuracy.
* Allows users to register and become recognized by the bot.
* Handles errors like a boss (mostly).

## Installation
1. [Download ZIP](https://github.com/liav22/PSBot/archive/master.zip) and exctract to any folder
2. Ensure you have Pyhon 3.7.1 and the required packages (see beginning of all `*.py` files)
3. Edit `config.ini` with the following:

⋅⋅⋅* Bot token - copy from [Discord Developer Portal](https://discordapp.com/developers/applications/)
⋅⋅⋅* Prefix - my personal pick is `~` but you can change it to your liking
⋅⋅⋅* Status - text message that the bot will show next to a "Playing" tag

4. Launch `main.py` with Python 3.7.1 using your system's console / terminal

## Usage
* Type `help` (with set prefix) in any Discord channel (the bot needs basic premissions) to see the command list.
* All errors are printed to console / terminal.
* User data is stored locally on `*.CSV` files in `/userdata/`.
