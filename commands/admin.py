"""
Various admin commands
"""

# Standard Python Modules
import random
import datetime

# Discord Modules
import discord
from discord.ext import commands

# ../modules
from modules import helpers, sql

async def grabmute(ctx, victim: discord.Member = None):
    """
    Grabs a mute from the DB

        Parameters:
            ctx (commands.Context): Context Reference
            victim (discord.Member): Member Reference

        Returns:
            mutee (discord.Member.ID): Returns the ID of the muted person, or false
    """
    if victim is None:
        return False
    mutee = (sql.select('mutes', ['id', int(victim.id), 'guild', int(victim.guild.id)]))[0]
    if not mutee:
        mutee = (sql.select('longmutes', ['id', int(victim.id), 'guild', int(victim.guild.id)]))[0]
    if not mutee:
        await ctx.send('They were never muted. If this wasnt supposed to be contact a coder', delete_after=3)
        return False
    return mutee

class Admin(commands.Cog):
    """
    Administration Commands
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='purge',
        brief='delete messages'
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, purge: int):
        """
        Purges upto 250 messages from a given channel

            Parameters:
                ctx (commands.Context): Context Reference
                purge (int<250): How many messages to purge
        """
        if purge > 250:
            return await ctx.send('You can only purge upto 250 messages', delete_after=3)

        await ctx.channel.purge(limit=purge, bulk=True)

    @commands.command(
        name='ban',
        brief='fancy ban'
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, victim: discord.Member = None):
        """
        Bans someone and send some funny text with it

            Parameters:
                ctx (commands.Context): Context Reference
                victim (discord.Member): Person to ban
        """
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
        """
        Kicks someone and send some funny text with it

            Parameters:
                ctx (commands.Context): Context Reference
                victim (discord.Member): Person to kick
        """
        if victim is None:
            temp = await ctx.send('You need to specify a person to kick')
            return await temp.delete(delay=3)

        funnys = [
                f'You are being exiled {victim.mention}',
                f'No. {victim.mention}',
                f'FBI open up! {victim.mention}',
                f'Your vibes are neutral... {victim.mention}!',
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
    async def mute(self, ctx, victim: discord.Member = None, *, time: str = None):
        """
        Mutes someone and DM's them the seconds they've been muted for

            Parameters:
                ctx (commands.Context): Context Reference
                victim (discord.Member): Person to mute
                time (str): Time in 1w1d1h1m1s to mute for
        """
        time = helpers.timeconv(time)

        if victim is None:
            return await ctx.send('You need to specify someone to mute', delete_after=3)

        if time is None:
            return await ctx.send('You need to specify a time', delete_after=3)

        muterole = discord.utils.get(ctx.guild.roles, name='Muted')
        if muterole is None:
            muterole = await ctx.guild.create_role(name='Muted', colour=discord.Colour.dark_gray(), reason='Mute setup')
            for channel in ctx.guild.channels:
                if channel.permissions_synced:
                    continue
                overrides = channel.overwrites_for(muterole)
                overrides.send_messages = False
                await channel.set_permissions(muterole, overwrite=overrides, reason='Mute setup')

        delta = (datetime.datetime.now() + datetime.timedelta(seconds=time)).strftime('%Y-%m-%d %H:%M:%S')
        muteparams = (int(victim.id), delta, int(ctx.guild.id), int(muterole.id))
        if sql.add('mutes', muteparams): # no escape
            embed = discord.Embed(title=f'You have been muted in: `{ctx.guild.name}` for `{time}s`')
            await victim.add_roles(muterole)
            await victim.send(embed=embed)

    @commands.command(
        name='unmute',
        brief='unmute a person'
    )
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, victim: discord.Member = None):
        """
        Mutes someone and DM's them the seconds they've been muted for

            Parameters:
                ctx (commands.Context): Context Reference
                victim (discord.Member): Person to unmute
        """
        if victim is None:
            return await ctx.send('You need to specify someone to unmute', delete_after=3)

        muteparams = await grabmute(ctx, victim)
        if muteparams:
            embed = discord.Embed(title=f'You have been unmuted from: `{victim.guild.name}`')
            muterole = victim.guild.get_role(muteparams[3])
            sql.remove('mutes', ['id', int(victim.id), 'guild', int(victim.guild.id)])
            await victim.remove_roles(muterole)
            await victim.send(embed=embed)

def setup(bot):
    """
    Setup the Admin Cog
    """
    bot.add_cog(Admin(bot))
