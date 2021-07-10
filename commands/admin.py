"""
Various admin commands
"""

import random
import time
import discord
from discord.ext import commands
from modules import helpers
import guildreader
from discord_slash import cog_ext


class Admin(commands.Cog):
    """
    Administration Commands
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        if ctx.guild:
            await ctx.message.delete()

    async def on_slash_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            return await ctx.send(error.message)
        if isinstance(error, discord.NotFound):
            return

    @cog_ext.cog_slash(
        name='purge',
        description='delete messages'
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

    @cog_ext.cog_slash(
        name='ban',
        description='fancy ban'
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

    @cog_ext.cog_slash(
        name='kick',
        description='fancy kick'
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

    @cog_ext.cog_slash(
        name='mute',
        description='mute a person in s,m,h,d,w'
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
            muterole = await helpers.generate_role("Muted", ctx.guild, discord.Color.dark_gray())
            await helpers.create_overrides(muterole.id, ctx.guild, {"send_messages": False})
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

    @cog_ext.cog_slash(
        name='unmute',
        description='unmute a person'
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
