""""
Common helper functions for bot
"""
import random
import discord

def embed(title: str = None, description: str = None, thumbnail: str = None, image: str = None, fields: list = None, inline: bool = True, color = discord.Colour.default()):
    """
    Helps with making clean embeds, has common needs
    """
    embedhelper = discord.Embed(title=title, description=description)
    embedhelper.color = color

    if thumbnail is not None:
        embedhelper.set_thumbnail(url=thumbnail)

    if image is not None:
        embedhelper.set_image(url=image)

    if fields is not None:
        for field in fields:
            embedhelper.add_field(name=field[0], value=field[1], inline=inline)

    if color == discord.Colour.default():
        embedhelper.color = random.randint(0, 0xffffff)

    return embedhelper

def timeconv(time: str = None):
    """
    Convert time to second from string(w,d,h,m,s)
    """
    if time is None:
        return 0

    timeseconds = 0
    timelist = time.split()
    for times in timelist:
        try:
            temp = times[:-1]
            int(temp)
        except:
            return None # Unknown Format was provided

        if times[-1] == "s":
            timeseconds += int(times[:-1])
        if times[-1] == "m":
            timeseconds += int(times[:-1]) * 60
        if times[-1] == "h":
            timeseconds += int(times[:-1]) * 3600
        if times[-1] == "d":
            timeseconds += int(times[:-1]) * 86400
        if times[-1] == "w":
            timeseconds += int(times[:-1]) * 604800
    return timeseconds
