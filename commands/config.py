"""
Handles all thing config
"""

import json
from pathlib import Path
from discord.ext import commands

class Configuration(commands.Cog):
    """
    Guild-Specific Configuration
    """
    def __init__(self, bot):
        self.bot = bot

    def read_file(self, ctx: commands.Context, key, default = None):
        """
        Get the guild configs will make a new file if not detected
        """
        data = {}
        if not Path(f'./data/guild_{key}.json').is_file():
            for guild in self.bot.guilds:
                data[str(guild.id)] = default

            with open(f'./data/guild_{key}.json', 'w') as fileout:
                json.dump(data, fileout, indent=4)

        with open(f'./data/guild_{key}.json', 'r') as filein:
            data = json.load(filein)

        return data[str(ctx.guild.id)]

    def write_file(self, ctx: commands.Context, key, value, default = None):
        """
        Get the guild configs will make a new file if not detected
        """
        data = {}
        if not Path(f'./data/guild_{key}.json').is_file():
            for guild in self.bot.guilds:
                data[str(guild.id)] = default

            with open(f'./data/guild_{key}.json', 'w') as fileout:
                json.dump(data, fileout, indent=4)

        with open(f'./data/guild_{key}.json', 'r') as filein:
            data = json.load(filein)

        data[str(ctx.guild.id)] = value

        with open(f'./data/guild_{key}.json', 'w') as fileout:
            json.dump(data, fileout, indent=4)

    @commands.command(
        name='prefix',
        brief='change the prefix of the bot',
    )
    @commands.has_permissions(administrator=True)
    async def changeprefix(self, ctx, prefix):
        """
        Change the prefix of the bot
        """
        self.write_file(ctx, 'prefix', prefix, '==')
        await ctx.send(f'Prefix changed to: {prefix}')
        botname = ctx.me.name
        await ctx.me.edit(nick=f'{prefix} | {botname}')

def setup(bot):
    """
    Add Configuration Cog
    """
    bot.add_cog(Configuration(bot))
