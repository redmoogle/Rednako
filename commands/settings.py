"""
Handles all thing config
"""

from discord.ext import commands
import discord
from modules import jsonreader

class Config(commands.Cog):
    """
    Guild-Specific Config
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='prefix',
        brief='change the prefix of the bot'
    )
    @commands.has_permissions(administrator=True)
    async def changeprefix(self, ctx, prefix):
        """
        Change the prefix of the bot
        """
        jsonreader.write_file(self.bot, ctx, 'prefix', prefix, '==')
        await ctx.send(f'Prefix changed to: {prefix}')
        botname = ctx.me.name
        await ctx.me.edit(nick=f'{prefix} | {botname}')

    @commands.command(
        name='djmode',
        brief='enable or disable djmode, nothing to turn it off'
    )
    @commands.has_permissions(administrator=True)
    async def djmode(self, ctx, djrole: discord.Role = None):
        if djrole is None:
            await ctx.send('Disabling DJ-Mode')
            jsonreader.write_file(self.bot, ctx, 'djmode', None, None)
            return

        await ctx.send(f'Enabling DJ-Config for role: {djrole.name}')
        jsonreader.write_file(self.bot, ctx, 'djmode', str(djrole.id), None)

def setup(bot):
    """
    Add Config Cog
    """
    bot.add_cog(Config(bot))
