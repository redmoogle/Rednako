"""
Handles all thing config
"""

from discord.ext import commands
import discord
import guildreader
from discord_slash import cog_ext


def isauthor(author):
    """Makes sure they're the command invoker"""
    def check(message) -> bool:
        return message.author == author
    return check


class Config(commands.Cog):
    """
    Guild-Specific Config
    """
    def __init__(self, bot):
        self.bot = bot

    async def on_slash_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingPermissions):
            return await ctx.send(error.message)

    @cog_ext.cog_slash(
        name='djmode',
        description='enable or disable djmode, nothing to turn it off'
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
            guildreader.write_file(ctx.guild.id, 'djmode', djrole)
            return await ctx.send('Disabling DJ-Mode')

        guildreader.write_file(ctx.guild.id, 'djmode', str(djrole.id))
        await ctx.send(f'Enabling DJ-Config for role: {djrole.name}')

    @cog_ext.cog_slash(
        name='errors',
        description='en/dis-able showing not found errors',
    )
    @commands.has_permissions(administrator=True)
    async def errors(self, ctx):
        """
        Shows or unshows commands not found error

            Parameters:
                ctx (commands.Context): Context Reference
        """
        toggle = guildreader.read_file(ctx.guild.id, 'settings')
        toggle['errors'] = not toggle['errors']
        guildreader.write_file(ctx.guild.id, 'settings', toggle)
        if not toggle:
            return await ctx.send("Disabling showing of command not found")
        return await ctx.send("Enabling showing of command not found")


def setup(bot):
    """
    Add Config Cog
    """
    bot.add_cog(Config(bot))
