"""
Handles all thing config
"""

from discord.ext import commands
import discord
import guildreader
from discord_slash import cog_ext
from markupsafe import string


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

    @cog_ext.cog_slash(
        name='addword',
        description='Add tracked words',
    )
    @commands.has_permissions(administrator=True)
    async def addword(self, ctx, word: str):
        """
        Add tracked words

            Parameters:
                ctx (commands.Context): Context Reference
                word (string): Word to track
        """
        wordjson: dict = guildreader.read_file(ctx.guild.id, 'wordcount')
        try:
            wordjson[word]
            return await ctx.send(f'{word} is already tracked')
        except KeyError:
            wordjson.setdefault(word, {})
            guildreader.write_file(ctx.guild.id, "wordcount", wordjson)
            return await ctx.send(f'Added {word} to tracked word list')

    @cog_ext.cog_slash(
        name='removeword',
        description='Removes and clears a tracked word',
    )
    @commands.has_permissions(administrator=True)
    async def errors(self, ctx, word: str):
        """
        remove tracked words

            Parameters:
                ctx (commands.Context): Context Reference
                word (string): Word to track
        """
        wordjson: dict = guildreader.read_file(ctx.guild.id, 'wordcount')
        try:
            del wordjson[word]
            guildreader.write_file(ctx.guild.id, "wordcount", wordjson)
            return await ctx.send(f'Removed {word} from tracking')
        except KeyError:
            return await ctx.send(f'{word} isnt tracked')

def setup(bot):
    """
    Add Config Cog
    """
    bot.add_cog(Config(bot))
