"""
Handles various money things
"""
#pylint: disable=bare-except

# Standard Python Modules
import random
import asyncio

# Discord Modules
from discord.ext import commands

# ../modules
from modules import jsonreader
from modules import helpers

def parse_duration(duration: int):
    """
    Parse duration into DD:HH:MM:SS
    """
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    duration = []
    _ = "" # used for zfill
    if days > 0:
        duration.append(f'{round(days)}:')
    if hours > 0:
        _ = str(round(hours))
        if days > 0:
            _ = _.zfill(2)
        _ += ":"
        duration.append(_)
    if minutes > 0:
        _ = str(round(minutes))
        if hours > 0:
            _ = _.zfill(2)
        _ += ":"
        duration.append(_)
    if seconds > 0:
        _ = str(round(seconds))
        if minutes > 0:
            _ = _.zfill(2)
        duration.append(_)

    return ''.join(duration)

class Economy(commands.Cog):
    """
    Economy Cog
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'Hold on there fellow heister, the cops are still hot on you wait some time({parse_duration(int(error.retry_after))})')

    @commands.command(
        name='payday',
        brief='steal money'
    )
    @commands.cooldown(1, 21600, commands.BucketType.member)
    async def payday(self, ctx):
        """
        ''Steals money''
        """
        guild_economy = jsonreader.read_file(ctx.guild.id, 'economy')
        try:
            money = guild_economy[str(ctx.author.id)]
        except:
            jsonreader.write_file(ctx.guild.id, 'economy', {str(ctx.author.id): 0})
            await ctx.send('Lets set you up a bank account!')
            await asyncio.sleep(5)
            await ctx.send('Done! You now have a OffSafe:tm: Account!')
            await asyncio.sleep(2)

        heisted = random.randint(5, 30)
        money += heisted
        guild_economy[str(ctx.author.id)] = money
        jsonreader.write_file(ctx.guild.id, 'economy', guild_economy)
        return await ctx.send(f'You just stole ${heisted}!')

    @commands.command(
        name='check',
        brief='check your offshore'
    )
    async def checking(self, ctx):
        """
        Check your offshore
        """
        guild_economy = jsonreader.read_file(ctx.guild.id, 'economy')
        try:
            money = guild_economy[str(ctx.author.id)]
        except:
            return await ctx.send('You\'re not registered with OffSafe:tm:!')

        info = [
            ['Total Balance: ', f'${money}']
        ]
        embed=helpers.embed(title=f'{ctx.author.name}\'s offshore account', image=ctx.author.avatar_url, fields=info)
        return await ctx.send(embed=embed)

def setup(bot):
    """does cog setup"""
    bot.add_cog(Economy(bot))
