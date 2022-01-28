"""
Handles all thing config
"""

from discord.commands import slash_command
from discord.ext import commands
import discord
import guildreader


def isauthor(author):
    """Makes sure they're the command invoker"""
    def check(message) -> bool:
        return message.author == author
    return check


class Config(discord.ext.commands.Cog):
    """
    Guild-Specific Config
    """
    def __init__(self, bot):
        self.bot = bot

    async def on_slash_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingPermissions):
            return await ctx.respond(error.message)

    @slash_command()
    @commands.has_permissions(administrator=True)
    async def djmode(self, ctx, djrole: discord.Role = None):
        """
        Limits playback modification to people with specified role

            Parameters:
                ctx (commands.Context): Context Reference
                djrole (discord.Role): Role to enable for
        """
        if djrole is None:
            guildreader.write_file(ctx.guild.id, 'djmode', djrole)
            return await ctx.respond('Disabling DJ-Mode')

        guildreader.write_file(ctx.guild.id, 'djmode', str(djrole.id))
        await ctx.respond(f'Enabling DJ-Config for role: {djrole.name}')

    @slash_command()
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
            return await ctx.respond("Disabling showing of command not found")
        return await ctx.respond("Enabling showing of command not found")

    @slash_command()
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
            return await ctx.respond(f'{word} is already tracked')
        except KeyError:
            wordjson.setdefault(word, {})
            guildreader.write_file(ctx.guild.id, "wordcount", wordjson)
            return await ctx.respond(f'Added {word} to tracked word list')

    @slash_command()
    @commands.has_permissions(administrator=True)
    async def removeword(self, ctx, word: str):
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
            return await ctx.respond(f'Removed {word} from tracking')
        except KeyError:
            return await ctx.respond(f'{word} isnt tracked')

def setup(bot):
    """
    Add Config Cog
    """
    bot.add_cog(Config(bot))
