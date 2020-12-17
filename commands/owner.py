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
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, purge: int):
        if(purge > 250):
            purge = 250
            return await ctx.send('You can only purge upto 250 messages', delete_after=3)

        async for message in ctx.channel.history(limit=purge):
            await message.delete()

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

def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the ping command to the bot
    # Note: The "setup" function has to be there in every cog file