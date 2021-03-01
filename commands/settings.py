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
        Changes the name of the bot to PREFIX | USERNAME and sets the guild prefix to that

            Parameters:
                ctx (commands.Context): Context Reference
                prefix (str): what to change the prefix to
        """
        jsonreader.write_file(ctx.guild.id, 'prefix', prefix)
        await ctx.send(f'Prefix changed to: {prefix}')
        botname = ctx.me.name
        await ctx.me.edit(nick=f'{prefix} | {botname}')

    @commands.command(
        name='djmode',
        brief='enable or disable djmode, nothing to turn it off'
    )
    @commands.has_permissions(administrator=True)
    async def djmode(self, ctx, djrole: discord.Role = None):
        """
        Enables DJ mode for the role provided

            Parameters:
                ctx (commands.Context): Context Reference
                djrole (discord.Role): Role to enable for
        """
        if djrole is None:
            jsonreader.write_file(ctx.guild.id, 'djmode', djrole)
            return await ctx.send('Disabling DJ-Mode')

        jsonreader.write_file(ctx.guild.id, 'djmode', str(djrole.id))
        await ctx.send(f'Enabling DJ-Config for role: {djrole.name}')

def setup(bot):
    """
    Add Config Cog
    """
    bot.add_cog(Config(bot))
