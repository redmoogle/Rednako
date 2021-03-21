"""
Random commands for the user
"""

# Discord Modules
import discord
from discord.ext import commands
import discordtextsanitizer as dts

# Github Module
import git

# Config Module
import config

# ../modules
from modules import helpers, jsonreader

config = config.Config('./config/bot.cfg')
repo = git.Repo(search_parent_directories=True)

class User(commands.Cog):
    """
    User Commands
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        if ctx.guild:
            await ctx.message.delete()

    @commands.command(
        name='say',
        brief='make the bot speak',
        aliases=['send', 'args']
    )
    async def args(self, ctx, *, args):
        """
        Sanitized Output from User Input

            Parameters:
                ctx (commands.Context): Context Reference
                args (str): What to send back
        """
        sanitized = dts.sanitize_mass_mentions(
            args, run_preprocess=True, users=True
        )
        await ctx.send(sanitized)

    @commands.command(
        name='serverinfo',
        brief='shows server info',
        aliases=['si']
    )
    async def serverinfo(self, ctx):
        """
        Embeds info about the guild it's ran in

            Parameters:
                ctx (commands.Context): Context Reference
        """
        guild = ctx.guild                           # grab guild
        textchannels = len(guild.text_channels)     # all text channels
        voicechannels = len(guild.voice_channels)   # all voice channels
        categorys = len(guild.categories)           # all categorys
        roles = len(guild.roles)                    # all roles
        members = len(guild.members)                # all members

        prefix = jsonreader.read_file(ctx.guild.id, 'settings')['prefix']

        info = [ # Makes adding easy and pretty
            ['Server Owner: ',      f'{guild.owner.name}#{guild.owner.discriminator}'],
            ['Server ID: ',         f'{guild.id}'],
            ['Categorys: ',         f'{categorys}'],
            ['Channels: ',          f'T: {textchannels} V: {voicechannels}'],
            ['Prefix: ',            f'{prefix}'],
            ['Roles: ',             f'{roles}'],
            ['Members: ',           f'{members}']
        ]

        embed=helpers.embed(title=guild.name, thumbnail=guild.icon_url, fields=info)
        await ctx.send(embed=embed)

    @commands.command(
        name='info',
        brief='botinfo',
        aliases=['globalinfo']
    )
    async def info(self, ctx):
        """
        Embeds info about the bot

            Parameters:
                ctx (commands.Context): Context Reference
        """
        self.bot = ctx.bot                       # shortcut for bot. var/bot is taken
        sha = repo.head.object.hexsha           # Hash of commit that the local files are
        totalservers = len(self.bot.guilds)      # List of all guilds, is a list so can len() it
        link = config['invitelink']             # Link to invite bot
        githublink = config['github']           # Github link

        totalmembers = 0
        for _ in self.bot.get_all_members():
            totalmembers += 1

        info = [ # Makes adding easy and pretty
                ['Bot Owner: ',         f'{self.bot.get_user(self.bot.owner_id)}'],
                ['Global Servers: ',    f'{totalservers}'],
                ['Global Members: ',    f'{totalmembers}'],
                ['Invite: ',            f'[Invite Bot]({link})'],
                ['Repository: ',        f'[Github]({githublink})'],
                ['Commit: ',            f'{sha}']
            ]

        embed=helpers.embed(
            title='Bot Statistics: ',
            thumbnail=self.bot.user.avatar_url,
            fields=info
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='ping',
        brief='ping discord api/bot'
    )
    async def ping(self, ctx):
        """
        Pings discord API and waits for heartbeat

            Parameters:
                ctx (commands.Context): Context Reference
        """
        embed = discord.Embed(title="Pong!", color=discord.Color.blurple())
        embed.add_field(name='API: ', value=(f'Latency: {round(self.bot.latency*1000)}ms'))
        await ctx.send(embed=embed)

def setup(bot):
    """
    Sets up user cog
    """
    bot.add_cog(User(bot))
