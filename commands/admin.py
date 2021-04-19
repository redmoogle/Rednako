"""
Various admin commands
"""

import random
import time
import discord
from discord.ext import commands
from modules import helpers
import guildreader


class Admin(commands.Cog):
    """
    Administration Commands
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        if ctx.guild:
            await ctx.message.delete()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, discord.NotFound):
            return

    @commands.command(
        name='purge',
        brief='delete messages'
    )
    @commands.has_permissions(manage_channels=True)
    async def purge(self, ctx, purge: int):
        """
        Purges up-to 250 messages from a given channel

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
    async def mute(self, ctx, victim: discord.Member = None, *, mutetime: str = None):
        """
        Mutes someone and DMs them the seconds they've been muted for

            Parameters:
                ctx (commands.Context): Context Reference
                victim (discord.Member): Person to mute
                mutetime (str): Time in 1w1d1h1m1s to mute for
        """
        mutetime = helpers.timeconv(mutetime)
        guilddata = guildreader.read_file(ctx.guild.id, 'muted')

        if victim is None:
            return await ctx.send('You need to specify someone to mute', delete_after=3)
        if mutetime is None:
            return await ctx.send('You need to specify a time', delete_after=3)

        muterole = discord.utils.get(ctx.guild.roles, id=guilddata['role'])
        if muterole is None:
            muterole = await ctx.guild.create_role(name='Muted', colour=discord.Colour.dark_gray(), reason='Mute setup')
            for channel in ctx.guild.channels:
                if channel.permissions_synced:
                    continue
                overrides = channel.overwrites_for(muterole)
                overrides.send_messages = False
                await channel.set_permissions(muterole, overwrite=overrides, reason='Mute setup')
            guilddata['role'] = muterole.id

        if str(victim.id) in guilddata:  # Extend Mute
            data = guilddata[str(victim.id)]
            data['expiration'] += mutetime
            await ctx.send(f'They have been muted for an additional {mutetime}s')
        else:
            data = {'expiration': time.time() + mutetime}
            await victim.add_roles(muterole)
            await victim.send(embed=discord.Embed(title=f'You have been muted in: `{ctx.guild.name}`'
                                                        f' for `{mutetime}s`'))
        guilddata[str(victim.id)] = data
        guildreader.write_file(ctx.guild.id, 'muted', guilddata)

    @commands.command(
        name='unmute',
        brief='unmute a person'
    )
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, victim: discord.Member = None):
        """
        Mutes someone and DMs them the seconds they've been unmuted

            Parameters:
                ctx (commands.Context): Context Reference
                victim (discord.Member): Person to unmute
        """
        if victim is None:
            return await ctx.send('You need to specify someone to unmute', delete_after=3)
        guilddata = guildreader.read_file(ctx.guild.id, 'muted')
        try:
            mutedata = guilddata[str(victim.id)]
            await victim.remove_roles(ctx.guild.get_role(mutedata['role']))
            await victim.send(embed=discord.Embed(
                title=f'You have been unmuted from: `{ctx.guild.name}`'
                )
            )
            del guilddata[str(victim.id)]
            guildreader.write_file(ctx.guild.id, 'muted', guilddata)
        except KeyError:
            await ctx.send("They aren't muted", delete_after=3)


def setup(bot):
    """
    Setup the Admin Cog
    """
    bot.add_cog(Admin(bot))
