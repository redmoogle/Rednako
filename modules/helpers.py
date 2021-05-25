""""
Common helper functions for bot
"""
import random
import discord


class NotFound(Exception):
    """
    The search parameters returned nothing
    """
    pass


def TypedError(expected, got):
    """
    Creates a helpful TypeError
    Args:
        expected: What should got should have been
        got: What the type was instead

    Returns:
        TypeError specifying what it got and what it wanted
    """
    raise TypeError(f"Expected {type(expected)} got {type(got)} instead")


def embed(title: str = None, description: str = None, thumbnail: str = None, image: str = None, fields: list = None,
          inline: bool = True, color=discord.Colour.default()) -> discord.Embed:
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
    embedhelper.colour = color

    if thumbnail is not None:
        embedhelper.set_thumbnail(url=thumbnail)

    if image is not None:
        embedhelper.set_image(url=image)

    if fields is not None:
        for field in fields:
            embedhelper.add_field(name=field[0], value=field[1], inline=inline)

    if color == discord.Colour.default():
        embedhelper.colour = random.randint(0, 0xffffff)

    return embedhelper


def timeconv(time: str = None) -> int:
    """
    Convert time from a 1w1d1h1m1s format to a int format

        Parameters:
            time (str): Time to convert in the format of 1w down to 1s

        Returns:
            time (int): Amount of time in seconds
    """
    if time is None:
        return 0

    if not isinstance(time, str):
        TypedError(str, time)

    timeseconds = 0
    timelist = time.split()
    for times in timelist:
        try:
            # Attempts to change the `7` from `7m` into a int, if it fails then it's not a valid format
            temp = times[:-1]
            int(temp)
        except ValueError:
            return None  # Unknown Format was provided

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


def parse_duration(duration, timefill: int = 0) -> str:
    """
    Parses seconds into DD:HH:MM:SS

        Parameters:
            duration (int): How long in seconds
            timefill (duration): duration to snap too (HH:MM:SS/HH:MM:SS)

        Returns:
            time, fill (tuple): DD:HH:MM:SS time in a str, how many divisors (:)
    """

    if not isinstance(duration, (int, float)):
        raise TypedError(int, duration)

    duration = int(duration)

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


def dividelist(lst: list, divisor, offset=0) -> list:
    """
    Slices a list while keeping the index stable

        Parameters:
            lst (list): list to slice
            divisor (int): What to divide(modulo) by
            offset (int): Offset of the index

        Returns:
            Sliced List (list): the list but sliced
    """

    if not isinstance(lst, list):
        TypedError(list, lst)
    indexoffset = 1
    for index in range(1, len(lst) + 1):
        if (index + offset) % divisor == 0:
            lst.pop(index - indexoffset)
            indexoffset += 1
    return lst


async def generate_role(rolename: str, guild: discord.Guild, color=None) -> discord.Role:
    """

    Args:
        rolename: Name of the role to generate
        guild: Guild to make it in
        color: Color of the role

    Returns:

    """
    if not isinstance(rolename, str):
        TypedError(str, rolename)

    if color:
        if isinstance(color, str):
            color = color.replace("#", "")
            colour = discord.Color(value=int(color, 16))
        elif isinstance(color, discord.Color):
            colour = color
        else:
            return TypedError(discord.Color, color)
        role = await guild.create_role(name=rolename, colour=colour, reason='Invoked Command')
    else:
        role = await guild.create_role(name=rolename, reason='Invoked Command')
    return role


async def create_overrides(role: int, guild: discord.Guild, overrides: dict) -> None:
    """

    Args:
        role: ID of the role
        guild: Guild to Search
        overrides: Overrides to make

    Returns:

    """
    if not isinstance(role, int):
        TypedError(int, role)

    if not isinstance(overrides, dict):
        TypedError(dict, overrides)

    role = discord.utils.get(guild.roles, id=role)
    if not role:
        raise NotFound("Role could not be found")
    for channel in guild.channels:
        if channel.permissions_synced:
            continue
        _overrides = channel.overwrites_for(role)
        _overrides.update(**overrides)
        await channel.set_permissions(role, overwrite=_overrides, reason='Invoked Command')
