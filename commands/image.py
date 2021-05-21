"""
Image commands
"""
import random
import discord
from discord.ext import commands
import nekos
from modules import helpers, animal


def grab_animal(_animal: str = None) -> str:
    """
    Validates that the animal is correct then grabs image

        Parameters:
            _animal: Name of a animal to grab

        Returns:
            url: Image URL
    """
    if _animal is None:
        return animal.Animals(None).image()
    if _animal == "bird":
        _animal = "birb"  # who shitposts in their module?
    if _animal not in ["cat", "dog", "koala", "fox", "birb", "red_panda", "panda", "racoon", "kangaroo"]:
        return None

    return animal.Animals(_animal).image()  # Grabs image


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
        await ctx.send(embed=helpers.embed(title='Neko', image=nekos.img('neko')))

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
        Grabs a cat... *yoink*

            Parameters:
                ctx (commands.Context): Context Reference
        """
        url = grab_animal('cat')
        randomtitles = [
            "Meow",
            "Mao",
            "Mreow",
            "Chirp",
            "Purr",
            "*Cat Noises*"
        ]
        random.shuffle(randomtitles)
        await ctx.send(embed=helpers.embed(title=randomtitles[0], image=url))

    @commands.command(
        name='animal'
    )
    async def animal(self, ctx, _animal: str = None):
        """`cat`, `dog`, `koala`, `fox`, `bird`, `red_panda`, `panda`, `racoon`, `kangaroo`"""
        url = grab_animal(_animal)
        if not url:
            return await ctx.send(f'{_animal} does not exist')

        if not _animal:
            _name = 'Random Animal Image'
        else:
            _name = f'Random {_animal.capitalize()} Image'

        await ctx.send(embed=helpers.embed(title=_name, image=url))


def setup(bot):
    """
    Add Image Cog
    """
    bot.add_cog(Image(bot))
