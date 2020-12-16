""""
Common helper functions for bot
"""
import random
import discord

def embed(title: str = None, description: str = None, thumbnail: str = None, image: str = None, fields: list = None, inline: bool = True, randcolor: bool = True):
    """
    Helps with making clean embeds, has common needs
    """
    embedhelper = discord.Embed(title=title, description=description)
    if thumbnail is not None:
        embedhelper.set_thumbnail(url=thumbnail)

    if image is not None:
        embedhelper.set_image(url=image)

    if fields is not None:
        for field in fields:
            embedhelper.add_field(name=field[0], value=field[1], inline=inline)

    if randcolor:
        embedhelper.color = random.randint(0, 0xffffff)

    return embedhelper
