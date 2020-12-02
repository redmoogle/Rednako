# Main Client Rednako
import discord
from discord.ext import commands
import asyncio
import config
import time

token = config.token

# Setting up config for open-source shenanigans

from discord.ext import commands


def get_prefix(client, message):

    prefixes = config.prefix    # sets the prefixes, u can keep it as an array of only 1 item if you need only one prefix

    if not message.guild:
        prefixes = config.prefix[0]  # Only allow first prefix as a prefix when in DMs, this is optional

    # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
    # Do `return prefixes` if u don't want to allow mentions instead of prefix.
    return commands.when_mentioned_or(*prefixes)(client, message)

intent = discord.Intents.all()

bot = commands.Bot(                         # Create a new bot
    command_prefix=get_prefix,              # Set the prefix
    description='Rednako Bot',              # Set a description for the bot
    owner_id=config.owner_id,               # Your unique User ID
    case_insensitive=True,                   # Make the commands case insensitive
    intents=intent
)

# case_insensitive=True is used as the commands are case sensitive by default
botcommands = [
'commands.ping',
'commands.Voice',
'commands.Music',
'commands.User'
]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    if(config.show_users):
        total = 0
        # Get all servers
        totalServers = bot.guilds
        totalMembers = bot.get_all_members()
        for x in totalMembers:
            total += 1
        print("Total servers " + str(len(totalServers)))
        print("Total members " + str(total))

    await bot.change_presence(activity=discord.Game(name=(config.default_activity).format(total, len(totalServers))))
    for command in botcommands:
        bot.load_extension(command)
    return

# Finally, login the bot
bot.run(token, bot=True, reconnect=True)



        
