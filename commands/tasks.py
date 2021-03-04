"""
Handles automated tasks
"""

# Standard Python Modules
from datetime import datetime

# Discord Modules
from discord.ext import commands, tasks
import discord

# ../modules
from modules import sql
from modules import jsonreader

tables = [
    ['mutes', ['id', 'INTEGER', 'experation', 'TIME', 'guild', 'INTEGER', 'role', 'INTEGER']],
    ['longmutes', ['id', 'INTEGER', 'experation', 'TIME', 'guild', 'INTEGER', 'role', 'INTEGER']]
]
configs = [["djmode", None], ["prefix", "=="], ["economy", {}], ['errors', True]]

class Task(commands.Cog):
    """
    Automatic Tasks
    """
    def __init__(self, bot):
        self.bot = bot
        self.mute.start()
        self.storage.start()
        for table in tables:
            sql.create_table(table=table[0], types=table[1], check_exist=True)

        for config in configs:
            jsonreader.create_file(bot, config[0], config[1])

    async def cog_before_invoke(self, ctx):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.mute.cancel()
        self.storage.cancel()

    @tasks.loop(seconds=5)
    async def mute(self):
        """
        Fast Iterating Database, removes mutes if under 0 seconds till experation

            Parameters:
                None
        """
        for data in sql.select('mutes'):
            time = data[1]
            guild = self.bot.get_guild(int(data[2]))
            role = guild.get_role(data[3])
            member = guild.get_member(data[0])
            delta = (datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - datetime.now()).total_seconds()
            if delta <= 0:
                sql.remove('mutes', ['id', int(member.id), 'guild', int(guild.id)])
                embed = discord.Embed(title=f'You have been unmuted from: `{guild.name}`')
                await member.send(embed=embed)
                await member.remove_roles(role)

    @tasks.loop(minutes=1)
    async def storage(self):
        """
        Slow iterating database to speed up the faster looping database

            Parameters:
                None
        """
        for row in sql.select('mutes'): # Move from active to storage
            time = row[1]
            delta = (datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - datetime.now()).total_seconds()
            if delta > 70: # Small buffer
                sql.add('longmutes', row)
                sql.remove('mutes', ['id', row[0], 'guild', row[2]])

        for row in sql.select('longmutes'): # Move from storage to active
            time = row[1]
            delta = (datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - datetime.now()).total_seconds()
            if delta <= 70:
                sql.add('mutes', row)
                sql.remove('longmutes', ['id', row[0], 'guild', row[2]])

def setup(bot):
    """
    Setup Task Cog
    """
    bot.add_cog(Task(bot))
