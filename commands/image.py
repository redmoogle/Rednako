"""
Image commands
"""
import random
import asyncio
import discord
from discord.ext import commands
import nekos
from modules import helpers
from modules import animal as animals
from discord_slash import cog_ext
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component


def grab_animal(_animal: str = None) -> str:
    """
    Validates that the animal is correct then grabs image

        Parameters:
            _animal: Name of a animal to grab

        Returns:
            url: Image URL
    """
    if not _animal:
        return animals.Animals(None).image()
    if _animal == "bird":
        _animal = "birb"  # who shitposts in their module?
    if _animal not in ["cat", "dog", "koala", "fox", "birb", "red_panda", "panda", "racoon", "kangaroo"]:
        return None

    return animals.Animals(_animal).image()  # Grabs image


class Image(commands.Cog):
    """
    Commands that send images
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        if ctx.guild:
            await ctx.message.delete()

    @cog_ext.cog_slash(
        name='avatar',
        description='Show user avatar',
    )
    async def avatar(self, ctx, user: discord.Member = None):
        """
        Sends a persons avatar

            Parameters:
                ctx (commands.Context): Context Reference
                user (discord.Member): Person to grab avatar from
        """
        # grabs their avatar and embeds it
        if user is None:
            user = ctx.author

        await ctx.send(embed=helpers.embed(title=f'{user}\'s Avatar', image=user.avatar_url))

    @cog_ext.cog_slash(
        name='cat',
        description='grabs cat'
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

    @cog_ext.cog_slash(
        name='animal',
        description='shows an animal'
    )
    async def animal(self, ctx):
        """`cat`, `dog`, `koala`, `fox`, `bird`, `red_panda`, `panda`, `racoon`, `kangaroo`"""
        selection = create_actionrow(create_select(
            options=[
                create_select_option("Random", value="None"),
                create_select_option("Cat", value="cat"),
                create_select_option("Dog", value="dog"),
                create_select_option("Koala", value="koala"),
                create_select_option("Fox", value="fox"),
                create_select_option("Bird", value="bird"),
                create_select_option("Red Panda", value="red_panda"),
                create_select_option("Panda", value="panda"),
                create_select_option("Racoon", value="racoon"),
                create_select_option("Kangaroo", value="kangaroo"),
            ],
            placeholder="Select or DIE",
            min_values=1,
            max_values=1
        ))
        msg = await ctx.send("Select an Animal...", components=[selection])
        try:
            result = await wait_for_component(self.bot, components=selection, timeout=15)
        except asyncio.TimeoutError:
            await msg.delete()
        animal = result.selected_options[0]
        if animal == "None":
            animal = None
        url = grab_animal(animal)
        if not url:
            return await ctx.send(f'{animal} does not exist')

        if not animal:
            _name = 'Random Animal Image'
        else:
            _name = f'Random {animal.capitalize()} Image'

        await msg.edit(content=None, embed=helpers.embed(title=_name, image=url), components=None)


def setup(bot):
    """
    Add Image Cog
    """
    bot.add_cog(Image(bot))
