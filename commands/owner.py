# pylint: disable=E1101
# error ignore for non-standard module

from discord.ext import commands
import config
import git
import discord
import subprocess
import random
import helpers
import asyncio
import datetime
import json
import sqlite3
from datetime import datetime, timedelta
connection = sqlite3.connect('database.db')
pointer = connection.cursor()
config = config.Config('./config.cfg')
repo = git.Repo(search_parent_directories=True)

async def repoembed():
    """
    returns a embed object of current repository commits
    """
    sha = repo.head.object.hexsha
    remotesha = repo.remotes.origin.fetch()[0].commit
    info = [
        ['Local Commit: ',  f'{sha}'],
        ['Github Commit: ', f'{remotesha}']
    ]
    
    embed=helpers.embed(title='Github Update: ', fields=info, inline=False)
    return embed

# New - The Cog class must extend the commands.Cog class
class Owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        await ctx.message.delete()
        
    @commands.command(
        name='update',
        brief='update bot'
    )
    @commands.is_owner()
    async def update(self, ctx):
        sha = repo.head.object.hexsha
        remotesha = repo.remotes.origin.fetch()[0].commit
        if(str(sha) != str(remotesha)):
            embed = await repoembed()
            await ctx.send(embed=embed)

        await self.bot.logout()
        subprocess.call(['bash', '/home/dakotamew/Rednako/commands/restart.sh'])
        exit()

    @commands.command(
        name='purge',
        brief='delete messages'
    )
    @commands.has_permissions(manage_channels=True)
    async def purge(self, ctx, purge: int):
        if(purge > 250):
            purge = 250
            return await ctx.send('You can only purge upto 250 messages', delete_after=3)

        await ctx.channel.purge(limit=purge, bulk=True)
    @commands.command(
        name='ban',
        brief='fancy ban'
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, victim: discord.Member = None):
        if victim is None:
            return await ctx.send('You need to specify a person to ban', delete_after=3)

        funnys = [
                f'Omae wa mou shindeiru... {victim.mention}',
                f'Enemy detected: {victim.mention}', 
                f'Die! {victim.mention}',
                f'Begone, {victim.mention}!',
                f'{victim.mention} has failed the vibe check'
                ]
        random.shuffle(funnys)
        await ctx.send(str(funnys[0]))
        await victim.ban()

    @commands.command(
        name='kick',
        brief='fancy kick'
    )
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, victim: discord.Member = None):
        if victim is None:
            temp = await ctx.send('You need to specify a person to kick')
            return await temp.delete(delay=3)

        funnys = [
                f'You are being exiled {victim.mention}',
                f'Stay in this hole until the end of time {victim.mention}', 
                f'I shan\'t look at you {victim.mention}',
                f'Stay away from me {victim.mention}!',
                f'{victim.mention} has failed the kneecap check'
                ]
        random.shuffle(funnys)
        await ctx.send(str(funnys[0]))
        await victim.kick()

    @commands.command(
        name='mute',
        brief='mute a person in s,m,h,d,w'
    )
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, victim: discord.Member = None, time: str = None):
        time = helpers.timeconv(time)
        try:
            pointer.execute(
            '''CREATE TABLE mutes
                (id INTEGER, experation TIME, guild INTEGER, role INTEGER)
                '''
            )
        except:
            pass

        if victim is None:
            return await ctx.send('You need to specificy someone to mute', delete_after=3)
        
        if time is None:
            return await ctx.send('You need to specificy a time', delete_after=3)

        muterole = discord.utils.get(ctx.guild.roles, name='Muted')
        if muterole is None:
            muterole = await ctx.guild.create_role(name='Muted', colour=discord.Colour.dark_gray(), reason='Mute setup')
            for channel in ctx.guild.channels:
                if(channel.permissions_synced):
                    continue
                overrides = channel.overwrites_for(muterole)
                overrides.send_messages = False
                await channel.set_permissions(muterole, overwrite=overrides, reason='Mute setup')

        await victim.add_roles(muterole)
        delta = (datetime.now() + timedelta(seconds=time))
        delta = delta.strftime('%Y-%m-%d %H:%M:%S')
        muteparams = (victim.id, delta, ctx.guild.id, muterole)
        pointer.execute(f'INSERT INTO mutes VALUES {muteparams};') # you're not escaping :^)
        connection.commit()
        for row in pointer.execute('SELECT * FROM mutes ORDER BY id;'):
            print(row)
        await asyncio.sleep(time)
        pointer.execute(f"DELETE FROM mutes WHERE id = '%s'" % victim.id) 
        connection.commit()
        for row in pointer.execute('SELECT * FROM mutes ORDER BY id;'):
            print(row)
        await victim.remove_roles(muterole)

def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the ping command to the bot
    # Note: The "setup" function has to be there in every cog file