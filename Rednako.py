# Main Client Rednako
import discord
from discord.ext import commands
import asyncio
import config

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


bot = commands.Bot(                         # Create a new bot
    command_prefix=get_prefix,              # Set the prefix
    description='Rednako Bot',              # Set a description for the bot
    owner_id=config.owner_id,               # Your unique User ID
    case_insensitive=True                   # Make the commands case insensitive
)

# case_insensitive=True is used as the commands are case sensitive by default
botcommands = [
'commands.ping',
'commands.Voice',
'commands.Music'
]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    await bot.change_presence(activity=discord.Game(name="Existin"))
    for command in botcommands:
        bot.load_extension(command)
    return



# Finally, login the bot
bot.run(token, bot=True, reconnect=True)



        
