"""
Rednako Public Discord Bot
Main Repository: https://github.com/redmoogle/Rednako
License: GPL-3.0
Make sure to set up config

Also important note. If you change default_activity
in the config make sure to update the .format in here

"""

# Standard Python Modules
import os
import sys
import json
import asyncio
from pathlib import Path

# Discord Modules
import discord
from discord.ext import commands
from pretty_help import PrettyHelp

# Config
import config

# Setting up config for open-source shenanigans
config = config.Config('./config/bot.cfg')
# Allows cogs to use the ./Modules folder
sys.path.append(os.path.abspath(__file__ + "/../modules"))

def get_prefix(client, message):
    """
    Load prefixes from json file if it exists, otherwise generate default prefix file
    """
    prefixes = {}
    defaultprefix = '=='
    if not message.guild:
        return commands.when_mentioned_or(defaultprefix)(client, message)

    if not Path('./data/guild_prefix.json').is_file(): # make sure it exists, if not generate default params
        for guild in bot.guilds:
            prefixes[str(guild.id)] = defaultprefix

        with open('./data/guild_prefix.json', 'w') as pfxfile:
            json.dump(prefixes, pfxfile, indent=4)

    with open('./data/guild_prefix.json', 'r') as pfxfile:
        prefixes = json.load(pfxfile)

    return prefixes[str(message.guild.id)] # Guild Specific Prefixes

bot = commands.Bot(                         # Create a new bot
    command_prefix=get_prefix,              # Set the prefix
    description='Rednako Public Bot',       # Set a description for the bot
    owner_id=config['owner_id'],            # Your unique User ID
    case_insensitive=True,                  # Make the commands case insensitive
    intents=discord.Intents.all(),          # Entirely Optional
    help_command=PrettyHelp()               # Default help command
)

botcommands = [
    'commands.music',
    'commands.user',
    'commands.admin',
    'commands.image',
    'commands.tasks',
    'commands.config'
]

@bot.event
async def on_ready():
    """Function is called when bot thinks it is fully online"""
    memlogging = await grab_members()
    print(f'Global Member Count: {memlogging[0]}')
    print(f'Global Servers: {memlogging[1]}')
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

    for command in botcommands:
        bot.load_extension(command)

async def update():
    """
    Updates the activity status of the bot
    """
    while True:
        await bot.wait_until_ready()
        memlogging = await grab_members()
        await bot.change_presence(
            activity=discord.Game(
                name=(config['default_activity']).format(memlogging[0], memlogging[1])
                )
            )
        await asyncio.sleep(90)

async def grab_members():
    """
    Grabs all the members that the bot can see

    Must have the config set to True
    Intents **MUST** Be set

    returns [members, servers]
    """
    await bot.wait_until_ready()
    if not config['show_users']:
        return [0, 0] # Return a blank array so it doesnt error out

    servers = len(bot.guilds)
    members = 0
    for _ in bot.get_all_members():
        members += 1
    return [members, servers]

@bot.event
async def on_guild_join(guild):
    """
    Called when the bot joins the guild
    """
    with open('./guild_prefix.json', 'r') as pfxfile:
        prefixes = json.load(pfxfile)

    prefixes[str(guild.id)] = '=='

    with open('./guild_prefix.json', 'w') as pfxfile:
        json.dump(prefixes, pfxfile, indent=4)

@bot.event
async def on_guild_remove(guild):
    """
    Called when the bot gets ejected/removed from the guild
    """
    with open('./guild_prefix.json', 'r') as pfxfile:
        prefixes = json.load(pfxfile)

    prefixes.pop(str(guild.id))

    with open('./guild_prefix.json', 'w') as pfxfile:
        json.dump(prefixes, pfxfile, indent=4)

# Finally, login the bot
bot.loop.create_task(update())
bot.run(config['token'], bot=True, reconnect=True)
