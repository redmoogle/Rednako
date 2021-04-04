"""
handles json files
"""

import json
from pathlib import Path


def create_file(bot, key: str, default, wipe: bool = False):
    """
    Creates a JSON config file for all guilds it can see with a default

        Parameters:
            bot (discord.Bot): Reference to the bot so it can get the guilds
            key (str): The `guild_key.json` to generate
            default (any): The value to put in as a placeholder
            wipe (bool): Wipe the files forcefully

        Returns:
            Success (bool): Did it succeed
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
    Reads a JSON file given the ID to find and key to look in

        Parameters:
            guild (str/int): the ID of the guild to return given key
            key (str): The key to look up

        Returns:
            data(any): The data for that guild and key
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
    Writes data to a guild JSON given a key

        Parameters:
            guild (str/int): ID of the guild
            key (str): The key to modify
            value (any): The value to write for that guild and key

        Returns:
            Success (bool): Did it succeed
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
    Removes a guild from a given key

        Parameters:
            guild (str/int): ID of the guild
            key (str): The key to modify

        Returns:
            Success (bool): Did it succeed
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
    Checks if a JSON key has been generated yet

        Parameters:
            key (str): The key to check

        Returns:
            Exist (bool): Does it exist
    """
    return Path(f'./data/guild_{key}.json').is_file()


def dump(key: str):
    """
    Dumps all the JSON given the key

        Parameters:
            key (str): The key to dump

        Returns:
            data (dict): The JSON data
    """
    data = {}

    with open(f'./data/guild_{key}.json', 'r') as filein:
        data = json.load(filein)

    return data
