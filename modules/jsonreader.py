"""
handles json files
"""

import json
from pathlib import Path
from discord.ext import commands

def create_file(bot, key: str, default, wipe: bool = False):
    """
    This is done to do this half inteligently this is used to "create" your config files
    """
    if Path(f'./data/guild_{key}.json').is_file() and not wipe: # allows for wiping of the config
        return False

    data = {}
    for guild in bot.guilds:
        data[str(guild.id)] = default

    with open(f'./data/guild_{key}.json', 'w') as fileout:
        json.dump(data, fileout, indent=4)
    return True

def read_file(ctx: commands.Context, key: str):
    """
    Get the guild configs for a key
    """
    data = {}

    if not Path(f'./data/guild_{key}.json').is_file():
        return False

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    return data[str(ctx.guild.id)]

def write_file(ctx: commands.Context, key: str, value):
    """
    Get the guild configs will make a new file if not detected
    """
    data = {}

    if not Path(f'./data/guild_{key}.json').is_file():
        return False

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    data[str(ctx.guild.id)] = value

    with open(f'./data/guild_{key}.json', 'w') as fileout:
        json.dump(data, fileout, indent=4)

def check_exist(key: str):
    """
    Checks if a given key exists
    """
    return Path(f'./data/guild_{key}.json').is_file()
