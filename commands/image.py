"""
Image commands
"""
import random
import requests
import discord
from discord.ext import commands
import nekos
from modules import helpers


class Image(commands.Cog):
    """
    Commands that send images
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        if ctx.guild:
            await ctx.message.delete()

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
        await ctx.send(embed=helpers.embed(title='Kitsune', image=nekos.img('fox_girl')))

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

        await ctx.send(embed=helpers.embed(title=f'{victim}\'s Avatar', image=victim.avatar_url))

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
        await ctx.send(embed=helpers.embed(title=randomtitles[0], image=data))


def setup(bot):
    """
    Add Image Cog
    """
    bot.add_cog(Image(bot))
