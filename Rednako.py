# Main Client Rednako
import config
import discord
from discord.ext import commands

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
    description='Rednako Bot',              # Set a description for the bot
    owner_id=config['owner_id'],               # Your unique User ID
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
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    if config['show_users']:
        total = 0
        # Get all servers
        totalservers = bot.guilds
        totalmembers = bot.get_all_members()
        for _ in totalmembers:
            total += 1
        print("Total servers " + str(len(totalservers)))
        print("Total members " + str(total))

    await bot.change_presence(
        activity=discord.Game(
            name=(config['default_activity']).format(total, len(totalservers))
            )
        )
    for command in botcommands:
        bot.load_extension(command)
    return

# Finally, login the bot
bot.run(token, bot=True, reconnect=True)
