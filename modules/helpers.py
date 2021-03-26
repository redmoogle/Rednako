""""
Common helper functions for bot
"""
import random
import discord

def embed(title: str = None, description: str = None, thumbnail: str = None, image: str = None, fields: list = None, inline: bool = True, color = discord.Colour.default()):
    """
    Creates a embed with various arguments.

        Parameters:
            title (str): Title of the embed
            description (str): Descriptipon of the embed
            thumbnail (str): Link to a image, displayed in the top right
            image (str): Link to a image, displayed at the bottom
            fields (list): Used to make lines [Line Name, Value]
            inline (bool): Is there one field for line or as many as can be jammed
            color (discord.Colour): color of the embed

        Returns:
            embed (discord.Embed): embed with all the arguments
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
    Convert time from a 1w1d1h1m1s format to a int format

        Parameters:
            time (str): Time to convert in the format of 1w down to 1s

        Returns:
            time (int): Amount of time in seconds
    """
    if time is None:
        return 0

    timeseconds = 0
    timelist = time.split()
    for times in timelist:
        try:
            # Attempts to change the `7` from `7m` into a int, if it fails then it's not a valid format
            temp = times[:-1]
            int(temp)
        except ValueError:
            return None # Unknown Format was provided

        # This converts if the above passes to actual seconds
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


def parse_duration(duration, timefill: int = 0):
    """
    Parses seconds into DD:HH:MM:SS

        Parameters:
            duration (int): How long in seconds
            timefill (duration): duration to snap too (HH:MM:SS/HH:MM:SS)

        Returns:
            time, fill (tuple): DD:HH:MM:SS time in a str, how many divisors (:)
    """

    try:
        duration = round(int(duration))
    except ValueError:
        return None # invalid format

    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    months, days = divmod(days, 30)
    years, months = divmod(months, 365)

    duration = []  # var reuse
    _ = ""  # used for zfill
    fill = 0
    if years or timefill >= 5:
        duration.append(f'{round(years)}:')
        fill += 1
    if months or timefill >= 4:
        duration.append(f'{round(months)}:')
        fill += 1
    if days or timefill >= 3:
        duration.append(f'{round(days)}:')
        fill += 1
    if hours or timefill >= 1:
        _ = str(round(hours))
        fill += 1
        if days or timefill >= 2 or hours >= 10:
            _ = _.zfill(2)
            fill += 1
        _ += ":"
        duration.append(_)
    _ = (str(round(minutes))).zfill(2)
    _ += ":"
    duration.append(_)
    _ = (str(round(seconds))).zfill(2)
    duration.append(_)
    return ''.join(duration), fill


def dividelist(inp, divisor, offset=0):
    """
    Slices a list while keeping the index stable

        Parameters:
            inp (list): list to slice
            divisor (int): What to divide(modulo) by
            offset (int): Offset of the index

        Returns:
            Sliced List (list): the list but sliced
    """
    indexoffset = 1
    for index in range(1, len(inp)+1):
        if (index+offset) % divisor == 0:
            inp.pop(index-indexoffset)
            indexoffset += 1
    return inp
