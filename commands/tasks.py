"""
Handles automated tasks
"""

# Standard Python Modules
import time

# Discord Modules
from discord.ext import commands, tasks
import discord

# ../modules
from modules import jsonreader

class Task(commands.Cog):
    """
    Automatic Tasks
    """
    def __init__(self, bot):
        self.bot = bot
        self.mute.start()
        self.check_guilds.start()
        for config in self.bot.configs:
            jsonreader.create_file(bot, config[0], config[1])

    async def cog_before_invoke(self, ctx):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.mute.cancel()
        self.storage.cancel()

    @tasks.loop(seconds=5)
    async def mute(self):
        """
        Fast Iterating JSON, removes mutes if under 0 seconds till experation

            Parameters:
                None
        """
        for guild in self.bot.guilds:
            data = jsonreader.read_file(guild.id, 'muted')
            for key in data:
                mutedata = data[key]
                if mutedata['expiration'] > time.time(): # this is probably marginally more efficent
                    continue
                member = key
                await member.remove_roles(
                    self.bot.get_guild(
                        guild.get_role(mutedata['role'])
                    )
                )
                await member.send(embed=discord.Embed(
                    title=f'You have been unmuted from: `{guild.name}`'
                    )
                )

    @tasks.loop(minutes=30)
    async def check_guilds(self):
        """
        Make sure all guilds have their configs and trims the files
        """
        _guilds = []
        for jsonfile in self.bot.configs:
            for guild in self.bot.guilds:
                _guilds.append(str(guild.id))
                if not jsonreader.read_file(guild.id, jsonfile[0]):
                    jsonreader.write_file(guild.id, jsonfile[0], jsonfile[1])

                if isinstance(jsonfile[1], dict):
                    test = jsonreader.read_file(guild.id, jsonfile[0])
                    for setting in jsonfile[1]:
                        try:
                            _ = test[setting]
                        except KeyError:
                            test[setting] = jsonfile[1][setting]
                    jsonreader.write_file(guild.id, jsonfile[0], test)

            raw = jsonreader.dump(jsonfile[0])
            for key in raw:
                if not key in _guilds:
                    jsonreader.remove(key, jsonfile[0])

def setup(bot):
    """
    Setup Task Cog
    """
    bot.add_cog(Task(bot))
