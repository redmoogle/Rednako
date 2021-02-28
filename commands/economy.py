"""
Handles various money things
"""
#pylint: disable=bare-except

# Standard Python Modules
import random

# Discord Modules
from discord.ext import commands

# ../modules
from modules import jsonreader
from modules import helpers

class Economy(commands.Cog):
    """
    Economy Cog
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='payday',
        brief='steal money'
    )
    async def payday(self, ctx):
        """
        ''Steals money''
        """
        guild_economy = jsonreader.read_file(ctx.guild.id, 'economy')
        try:
            money = guild_economy[str(ctx.author.id)]
        except:
            jsonreader.write_file(ctx.guild.id, 'economy', {str(ctx.author.id): 0})
            return await ctx.send('Lets set you up a bank account!')

        heisted = random.randint(5, 30)
        money[str(ctx.author.id)] += heisted
        jsonreader.write_file(ctx.guild.id, 'economy', money)
        return await ctx.send(f'You just stole {heisted}!')

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
            'Money: ', f'{money}'
        ]
        embed=helpers.embed(title=f'{ctx.author.name}\'s offshore account', image=ctx.author.avatar_url, fields=info)
        return await ctx.send(embed=embed)

def setup(bot):
    """does cog setup"""
    bot.add_cog(Economy(bot))
