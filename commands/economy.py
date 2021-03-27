"""
Handles various money things
"""
import random
import asyncio
from discord.ext import commands
from modules import helpers, jsonreader


class Economy(commands.Cog):
    """
    Economy Cog
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'Hold on there fellow heister, the cops are still hot on you wait some time({helpers.parse_duration(int(error.retry_after))[0]})')

    @commands.command(
        name='payday',
        brief='steal money'
    )
    @commands.cooldown(1, 21600, commands.BucketType.member)
    async def payday(self, ctx):
        """
        Steals money from somewhere random

            Parameters:
                ctx (commands.Context): Context Reference
        """
        guild_economy = jsonreader.read_file(ctx.guild.id, 'economy')
        try:
            money = guild_economy[str(ctx.author.id)]
        except KeyError:
            jsonreader.write_file(ctx.guild.id, 'economy', {str(ctx.author.id): 0})
            await ctx.send('Lets set you up a bank account!')
            await asyncio.sleep(5)
            await ctx.send('Done! You now have a OffSafe:tm: Account!')
            await asyncio.sleep(2)
            return

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
        Checks how much money that have

            Parameters:
                ctx (commands.Context): Context Reference
        """
        guild_economy = jsonreader.read_file(ctx.guild.id, 'economy')
        try:
            money = guild_economy[str(ctx.author.id)]
        except KeyError:
            return await ctx.send('You\'re not registered with OffSafe:tm:!')

        info = [
            ['Total Balance: ', f'${money}']
        ]
        embed=helpers.embed(title=f'{ctx.author.name}\'s offshore account', image=ctx.author.avatar_url, fields=info)
        return await ctx.send(embed=embed)


def setup(bot):
    """does cog setup"""
    bot.add_cog(Economy(bot))
