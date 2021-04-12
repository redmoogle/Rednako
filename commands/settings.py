"""
Handles all thing config
"""

from discord.ext import commands
import discord
import guildreader


def isauthor(author):
    """Makes sure they're the command invoker"""
    def check(message):
        return message.author == author
    return check


class Config(commands.Cog):
    """
    Guild-Specific Config
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='prefix',
        brief='change the prefix of the bot'
    )
    @commands.has_permissions(administrator=True)
    async def changeprefix(self, ctx, prefix):
        """
        Changes the name of the bot to PREFIX | USERNAME and sets the guild prefix to that

            Parameters:
                ctx (commands.Context): Context Reference
                prefix (str): what to change the prefix to
        """
        guildreader.write_file(ctx.guild.id, 'prefix', prefix)
        await ctx.send(f'Prefix changed to: {prefix}')
        await ctx.me.edit(nick=f'{prefix} | {ctx.me.name}')

    @commands.command(
        name='djmode',
        brief='enable or disable djmode, nothing to turn it off'
    )
    @commands.has_permissions(administrator=True)
    async def djmode(self, ctx, djrole: discord.Role = None):
        """
        Enables DJ mode for the role provided

            Parameters:
                ctx (commands.Context): Context Reference
                djrole (discord.Role): Role to enable for
        """
        if djrole is None:
            guildreader.write_file(ctx.guild.id, 'djmode', djrole)
            return await ctx.send('Disabling DJ-Mode')

        guildreader.write_file(ctx.guild.id, 'djmode', str(djrole.id))
        await ctx.send(f'Enabling DJ-Config for role: {djrole.name}')

    @commands.command(
        name='showerrors',
        brief='en/dis-able showing not found errors'
    )
    @commands.has_permissions(administrator=True)
    async def errors(self, ctx):
        """
        Shows or unshows commands not found error

            Parameters:
                ctx (commands.Context): Context Reference
        """
        toggle = guildreader.read_file(ctx.guild.id, 'settings')
        toggle['errors'] = not toggle['errors']
        guildreader.write_file(ctx.guild.id, 'settings', toggle)
        if not toggle:
            return await ctx.send("Disabling showing of command not found")
        return await ctx.send("Enabling showing of command not found")

    @commands.command(
        name='enablexp',
        brief='en/dis-able XP system'
    )
    @commands.has_permissions(administrator=True)
    async def xpenable(self, ctx):
        """
        enables or disables that guilds xp system

            Parameters:
                ctx (commands.Context): Context Reference
        """
        toggle = guildreader.read_file(ctx.guild.id, 'xp')
        toggle['enabled'] = not toggle['enabled']
        guildreader.write_file(ctx.guild.id, 'xp', toggle)
        if toggle['enabled']:
            return await ctx.send("Enabling EXP tracking")
        return await ctx.send("Disabling EXP tracking")

    @commands.command(
        name='muterole',
        brief='set the role for the mute'
    )
    @commands.has_permissions(kick_members=True)
    async def muterole(self, ctx, role: discord.Role = None):
        data = guildreader.read_file(ctx.guild.id, 'muted')
        if role is None:
            await ctx.send('No mute role found... Reset? y/n')
            response = await self.bot.wait_for('message', check=isauthor(ctx.author), timeout=15)
            if response.content in ['y', 'yes']:
                muterole = await ctx.guild.create_role(name='Muted', colour=discord.Colour.dark_gray(),
                                                       reason='Mute setup')
                for channel in ctx.guild.channels:
                    if channel.permissions_synced:
                        continue
                    overrides = channel.overwrites_for(muterole)
                    overrides.send_messages = False
                    await channel.set_permissions(muterole, overwrite=overrides, reason='Mute setup')
                    data['role'] = muterole.id
                    guildreader.write_file(ctx.guild.id, 'muted', data)

                await ctx.send('Mute role reset')
            return

        await ctx.send(f'Mute role set for {role.name}')
        data['role'] = role.id
        guildreader.write_file(ctx.guild.id, 'muted', data)


def setup(bot):
    """
    Add Config Cog
    """
    bot.add_cog(Config(bot))
