# pylint: disable=E1101
# error ignore because pylint is retarted

# Handle tasks
from discord.ext import commands, tasks
from datetime import datetime
import discord
import asyncio
import sqlite3

connection = sqlite3.connect('database.db')
pointer = connection.cursor()

tables = [
    '''CREATE TABLE IF NOT EXISTS mutes
        (id INTEGER, experation TIME, guild INTEGER, role INTEGER)
    ''',
    '''CREATE TABLE IF NOT EXISTS longmutes
        (id INTEGER, experation TIME, guild INTEGER, role INTEGER)
    '''
]

class Task(commands.Cog):
    """
    Automatic Tasks
    """
    def __init__(self, bot):
        for table in tables:
            pointer.execute(table)
        self.bot = bot
        self.mute.start()
        self.storage.start()

    async def cog_before_invoke(self, ctx):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.mute.cancel()
        self.storage.cancel()

    @tasks.loop(seconds=5)
    async def mute(self):
        for data in pointer.execute('SELECT * FROM mutes ORDER BY id;'):
            member = guild.get_member(data[0])
            time = data[1]
            guild = self.bot.get_guild(data[2])
            if(guild):
                role = guild.get_role(data[3])
            delta = (datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - datetime.now()).total_seconds()
            if(delta <= 0):
                print(f'SQL-DELETE: {data}')
                pointer.execute(f'DELETE FROM mutes WHERE id = {int(member.id)} AND guild = {int(guild.id)}')
                connection.commit()
                embed = discord.Embed(title=f'You have been unmuted from: `{guild.name}`')
                await member.send(embed=embed)
                await member.remove_roles(role)

    @tasks.loop(minutes=1)
    async def storage(self):
        """
        Move long mutes into storage to keep the 5 second task fast
        """
        for row in pointer.execute('SELECT * FROM mutes ORDER BY id;'): # Move from active to storage
            time = row[1]
            delta = (datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - datetime.now()).total_seconds()
            if(delta > 70): # Small buffer
                print(f'SQL-MOVE: {row}')
                pointer.execute(f'INSERT INTO longmutes VALUES {row};')
                pointer.execute(f'DELETE FROM mutes WHERE id = {row[0]} and guild = {row[2]}')

        for row in pointer.execute('SELECT * FROM longmutes ORDER BY id;'): # Move from storage to active
            time = row[1]
            delta = (datetime.strptime(time, '%Y-%m-%d %H:%M:%S') - datetime.now()).total_seconds()
            if(delta <= 70):
                print(f'SQL-MOVE: {row}')
                pointer.execute(f'INSERT INTO mutes VALUES {row};')
                pointer.execute(f'DELETE FROM longmutes WHERE id = {row[0]} and guild = {row[2]}')
        connection.commit()


def setup(bot):
    bot.add_cog(Task(bot))


