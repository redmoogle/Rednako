"""
Rednako Public Discord Bot
Main Repository: https://github.com/redmoogle/Rednako
License: GPL-3.0
Make sure to set up config

Also important note. If you change default_activity
in the config make sure to update the .format in here

"""
import asyncio
import config
import discord
from discord.ext import tasks, commands

# Setting up config for open-source shenanigans
config = config.Config('config.cfg')
token = config['token']

def get_prefix(client, message):
    """Returns the prefix of the bot (stored in config.cfg)"""

    prefixes = list(config['prefix'])    # grab prefix from config

    if not message.guild:
        prefixes = list(config['prefix'])  # Only allow first prefix when in DMs, optional
        prefixes = prefixes[0]

    # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
    # Do `return prefixes` if u don't want to allow mentions instead of prefix.
    return commands.when_mentioned_or(*prefixes)(client, message)

intent = discord.Intents.all()

bot = commands.Bot(                         # Create a new bot
    command_prefix=get_prefix,              # Set the prefix
    description='Rednako Public Bot',       # Set a description for the bot
    owner_id=config['owner_id'],            # Your unique User ID
    case_insensitive=True,                  # Make the commands case insensitive
    intents=intent                          # Entirely Optional
)

# case_insensitive=True is used as the commands are case sensitive by default
botcommands = [
    'commands.ping',
    'commands.voice',
    'commands.music',
    'commands.user'
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
    return

async def update():
    """
    Updates the activity status of the bot
    """
    while True:
        print('tried')
        await bot.wait_until_ready()
        print('ready')
        while not bot.is_closed:
            print('not closed')
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

# Finally, login the bot
bot.loop.create_task(update())
bot.run(token, bot=True, reconnect=True)
