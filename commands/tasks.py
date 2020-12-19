# Handle tasks
from discord.ext import commands
from datetime import datetime
import discord
import asyncio
import sqlite3

connection = sqlite3.connect('database.db')
pointer = connection.cursor()

class Task(commands.Cog):
    """
    Automatic Tasks
    """
    def __init__(self, bot):
        self.bot = bot
        self.mutetask = self.bot.loop.create_task(self.mute())

    async def cog_before_invoke(self, ctx):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.mutetask.cancel()

    async def mute(self):
        for row in pointer.execute('SELECT * FROM mutes ORDER BY id;'):
            print(f'SQL-LOAD: {row}')
            _data = row # Prevents data-overriding
            guild = self.bot.get_guild(_data[2])
            member = guild.get_member(_data[0])
            role = guild.get_role(_data[3])
            time = _data[1]
            delta = (datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - datetime.now()).total_seconds()
            if(delta <= 0):
                print(f'SQL-DELETE: {row}')
                pointer.execute(f'DELETE FROM mutes WHERE id = {member.id} AND guild = {guild.id}')
                connection.commit()
                embed = discord.Embed(title=f'You have been unmuted from: `{guild.name}`')
                await member.send(embed=embed)
                await member.remove_roles(role)
        await asyncio.sleep(15)

def setup(bot):
    bot.add_cog(Task(bot))


