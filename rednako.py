"""
Rednako Public Discord Bot
Main Repository: https://github.com/redmoogle/Rednako
License: GPL-3.0
Make sure to set up config

Also important note. If you change default_activity
in the config make sure to update the .format in here

"""
import asyncio
import sqlite3
import config
import discord
from discord.ext import commands
from pretty_help import PrettyHelp
import json
from pathlib import Path

# Setting up config for open-source shenanigans
config = config.Config('config.cfg')
token = config['token']
connection = sqlite3.connect('database.db')
pointer = connection.cursor()

def get_prefix(client, message):
    prefixes = {}
    if not Path('prefixes.json').is_file(): # make sure it exists, if not generate default params
        for guild in bot.guilds:
            prefixes[str(guild.id)] = '=='

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
    
    with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

    return prefixes[str(message.guild.id)] # Guild Specific Prefixes

intent = discord.Intents.all()

bot = commands.Bot(                         # Create a new bot
    command_prefix=get_prefix,              # Set the prefix
    description='Rednako Public Bot',       # Set a description for the bot
    owner_id=config['owner_id'],            # Your unique User ID
    case_insensitive=True,                  # Make the commands case insensitive
    intents=intent,                         # Entirely Optional
    help_command=PrettyHelp()               # Default help command
)

# case_insensitive=True is used as the commands are case sensitive by default
botcommands = [
    'commands.music',
    'commands.user',
    'commands.admin',
    'commands.image',
    'commands.tasks'
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
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '=='

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@bot.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

# Finally, login the bot
bot.loop.create_task(update())
bot.run(token, bot=True, reconnect=True)
