#pylint: disable=wrong-import-position
# have to do this because I have to append the path first

"""
Rednako Public Discord Bot
Main Repository: https://github.com/redmoogle/Rednako
License: GPL-3.0
Make sure to set up config

Also important note. If you change default_activity
in the config make sure to update the .format in here

"""

# Standard Python Modules
import asyncio

# Discord Modules
import discord
from discord.ext import commands
from pretty_help import PrettyHelp

# Config
import config

# ./modules
from modules import jsonreader

# Setting up config for open-source shenanigans
config = config.Config('./config/bot.cfg')
DEFAULTPREFIX = '=='

def get_prefix(botpfx, ctx):
    """
    Load prefixes from json file if it exists, otherwise generate default prefix file
    """
    if not ctx.guild:
        return commands.when_mentioned_or(DEFAULTPREFIX)(botpfx, ctx)

    if not jsonreader.check_exist('prefix'): # File will be created shortly
        return commands.when_mentioned

    return jsonreader.read_file(ctx.guild.id, 'prefix') # Guild Specific Preset

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
    'commands.settings'
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
    jsonreader.write_file(guild.id, 'prefix', DEFAULTPREFIX)

@bot.event
async def on_guild_remove(guild):
    """
    Called when the bot gets ejected/removed from the guild
    """
    jsonreader.remove(guild.id, 'prefix')

# Finally, login the bot
bot.loop.create_task(update())
bot.run(config['token'], bot=True, reconnect=True)
