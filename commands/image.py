"""
Image commands
"""

# Standard Python Modules
import random
import requests

# Discord Modules
import discord
from discord.ext import commands

# Misc Modules
import nekos

# ../modules
from modules import helpers

# Dont worry I can feel the disappointment from my computer
class Image(commands.Cog):
    """
    Commands that send images
    """
    def __init__(self, bot):
        self.bot = bot

    # Define a new command
    @commands.command(
        name='neko',
        brief='send embedded catgirl'
    )
    async def neko(self, ctx):
        """
        Sends a catgrill embed

            Parameters:
                ctx (commands.Context): Context Reference
        """
        embed=helpers.embed(title='Neko', image=nekos.img('neko'))
        await ctx.send(embed=embed)

    @commands.command(
        name='kitsune',
        brief='send embedded foxgirl'
    )
    async def kitsune(self, ctx):
        """
        Sends a foxgrill embed

            Parameters:
                ctx (commands.Context): Context Reference
        """
        embed=helpers.embed(title='Kitsune', image=nekos.img('fox_girl'))
        await ctx.send(embed=embed)

    @commands.command(
        name='avatar',
        brief='Show user avatar',
        aliases=['avtr']
    )
    async def avatar(self, ctx, victim: discord.Member = None):
        """
        Sends a persons avatar

            Parameters:
                ctx (commands.Context): Context Reference
                victim (discord.Member): Person to grab avatar from
        """
        # grabs their avatar and embeds it
        if victim is None:
            victim = ctx.author

        embed=helpers.embed(title=f'{victim}\'s Avatar', image=victim.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(
        name='cat',
        brief='grabs cat'
    )
    async def cat(self, ctx):
        """
        Sends a persons avatar

            Parameters:
                ctx (commands.Context): Context Reference
        """
        response = requests.get('https://aws.random.cat/meow')
        data = (response.json())['file']
        randomtitles = [
            "Meow",
            "Mao",
            "Mreow",
            "Chirp",
            "Purr",
            "*Cat Noises*"
        ]
        random.shuffle(randomtitles)
        embed = helpers.embed(title=randomtitles[0], image=data)
        await ctx.send(embed=embed)

def setup(bot):
    """
    Add Image Cog
    """
    bot.add_cog(Image(bot))
