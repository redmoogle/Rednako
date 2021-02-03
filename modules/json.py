"""
handles json files
"""

import json
from pathlib import Path
from discord.ext import commands

def read_file(bot, ctx: commands.Context, key, default = None):
    """
    Get the guild configs will make a new file if not detected
    """
    data = {}
    if not Path(f'./data/guild_{key}.json').is_file():
        for guild in bot.guilds:
            data[str(guild.id)] = default

        with open(f'./data/guild_{key}.json', 'w') as fileout:
            json.dump(data, fileout, indent=4)

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    return data[str(ctx.guild.id)]

def write_file(bot, ctx: commands.Context, key, value, default = None):
    """
    Get the guild configs will make a new file if not detected
    """
    data = {}
    if not Path(f'./data/guild_{key}.json').is_file():
        for guild in bot.guilds:
            data[str(guild.id)] = default

        with open(f'./data/guild_{key}.json', 'w') as fileout:
            json.dump(data, fileout, indent=4)

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    data[str(ctx.guild.id)] = value

    with open(f'./data/guild_{key}.json', 'w') as fileout:
        json.dump(data, fileout, indent=4)
