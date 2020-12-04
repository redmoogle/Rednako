import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import youtube_dl
import asyncio

# New - The Cog class must extend the commands.Cog class
class Voice(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    # Define a new command
    @commands.command(
        name='joinvoice',
        description='Join the voice channel your in',
        aliases=['jv']
    )
    async def joinvoice_command(self, ctx):
        connected = ctx.author.voice
        # Gets users channel
        if(connected):
            await connected.channel.connect()
        # and join it
        
    # Define a new command
    @commands.command(
        name='leavevoice',
        description='Leave the voice channel your in',
        aliases=['lv']
    )
    async def leavevoice_command(self, ctx):
        await ctx.voice_client.disconnect() # Big brain move took me 30 minutes to debug

def setup(bot):
    bot.add_cog(Voice(bot))
    # Adds the ping command to the bot
    # Note: The "setup" function has to be there in every cog file
