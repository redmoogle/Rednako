import random
import discord
from discord.ext import commands

def embedHelper(title: str = None, thumbnail: str = None, image: str = None, fields: list = None, inline: bool = True, randColor: bool = True):
    """
    Helps with making clean embeds, has common needs
    """
    embedhelper = discord.Embed(title=title)
    if thumbnail is not None:
        embedhelper.set_thumbnail(url=thumbnail)

    if image is not None:
        embedhelper.set_image(url=image)

    if fields is not None:
        for field in fields:
            embedhelper.add_field(name=field[0], value=field[1], inline=inline)

    if randColor:
        embedhelper.color = random.randint(0, 0xffffff)

    return embedhelper
