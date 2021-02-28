"""
handles json files
"""

import json
from pathlib import Path

def create_file(bot, key: str, default, wipe: bool = False):
    """
    This is done to do this half inteligently this is used to "create" your config files
    """
    if Path(f'./data/guild_{key}.json').is_file() and not wipe: # allows for wiping of the config
        return False

    data = {}

    for guild in bot.guilds:
        _guild = str(guild.id)
        data[_guild] = default

    with open(f'./data/guild_{key}.json', 'w') as fileout:
        json.dump(data, fileout, indent=4)
    return True

def read_file(guild, key: str):
    """
    Get the guild configs for a key
    """
    data = {}
    guild = str(guild)

    if not Path(f'./data/guild_{key}.json').is_file():
        return False

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    return data[guild]

def write_file(guild, key: str, value):
    """
    Get the guild configs will make a new file if not detected
    """
    data = {}
    guild = str(guild)

    if not Path(f'./data/guild_{key}.json').is_file():
        return False

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    data[guild] = value

    with open(f'./data/guild_{key}.json', 'w') as fileout:
        json.dump(data, fileout, indent=4)
    return True

def remove(guild, key: str):
    """
    Removes a given guild from the file
    """
    data = {}
    guild = str(guild)

    if not Path(f'./data/guild_{key}.json').is_file():
        return False

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    data.pop(guild)

    with open(f'./data/guild_{key}.json', 'w') as fileout:
        json.dump(data, fileout, indent=4)

    return True

def check_exist(key: str):
    """
    Checks if a given key exists
    """
    return Path(f'./data/guild_{key}.json').is_file()

def dump(key: str):
    """
    Dumps json data
    """
    data = {}

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    return data