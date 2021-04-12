"""
Handles automated tasks
"""
import time
from discord.ext import commands, tasks
import discord
import guildreader


class Task(commands.Cog):
    """
    Automatic Tasks
    """
    def __init__(self, bot):
        self.bot = bot
        self.mute.start()
        self.check_guilds.start()
        for config in self.bot.configs:
            guildreader.create_file(bot, config[0], config[1])

    async def cog_before_invoke(self, ctx):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.mute.cancel()
        self.check_guilds.cancel()

    @tasks.loop(seconds=5)
    async def mute(self):
        """
        Fast Iterating JSON, removes mutes if under 0 seconds till expiration
        """
        for guild in self.bot.guilds:
            data = guildreader.read_file(guild.id, 'muted')
            guildrole = data['role']
            for key in list(data):
                if key == 'role':
                    continue
                mutedata = data[key]
                if mutedata['expiration'] > time.time():  # this is probably marginally more efficient
                    continue
                member = await guild.fetch_member(key)
                await member.remove_roles(
                        guild.get_role(guildrole)
                )
                await member.send(embed=discord.Embed(
                    title=f'You have been unmuted from: `{guild.name}`'
                    )
                )
                del data[key]
                guildreader.write_file(guild.id, 'muted', data)

    @tasks.loop(minutes=30)
    async def check_guilds(self):
        """
        Make sure all guilds have their configs and trims the files
        """
        _guilds = []
        for jsonfile in self.bot.configs:
            for guild in self.bot.guilds:
                _guilds.append(str(guild.id))
                if not guildreader.read_file(guild.id, jsonfile[0]):
                    guildreader.write_file(guild.id, jsonfile[0], jsonfile[1])

                if isinstance(jsonfile[1], dict):
                    test = guildreader.read_file(guild.id, jsonfile[0])
                    for setting in jsonfile[1]:
                        try:
                            _ = test[setting]
                        except KeyError:
                            test[setting] = jsonfile[1][setting]
                    guildreader.write_file(guild.id, jsonfile[0], test)

            raw = guildreader.dump(jsonfile[0])
            for key in raw:
                if key in _guilds:
                    continue
                guildreader.remove(key, jsonfile[0])


def setup(bot):
    """
    Setup Task Cog
    """
    bot.add_cog(Task(bot))
