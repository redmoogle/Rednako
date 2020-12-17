# pylint: disable=E1101
# error ignore for non-standard module

from discord.ext import commands
import discord
import config
import random
import git
import helpers
config = config.Config('./config.cfg')
repo = git.Repo(search_parent_directories=True)

# New - The Cog class must extend the commands.Cog class
class User(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        await ctx.message.delete()

    @commands.command(
        name='say',
        brief='make the bot speak',
        aliases=['send', 'args']
    )
    async def args(self, ctx, *, args):
        await ctx.send(args)

    @commands.command(
        name='serverinfo',
        brief='shows server info',
        aliases=['si']
    )
    async def serverinfo(self, ctx):
        guild = ctx.guild           # grab guild
        textchannels = 0            # all text channels
        voicechannels = 0           # all voice channels
        categorys = 0               # all categorys
        roles = 0                   # all roles
        members = 0                 # all membersr

        for _ in guild.voice_channels:
            voicechannels += 1

        for _ in guild.text_channels:
            textchannels += 1
        
        for _ in guild.categories:
            categorys += 1

        for _ in guild.roles:
            roles += 1

        for _ in guild.members: #Theres a reason this is async
            members += 1

        info = [ # Makes adding easy and pretty
            ['Server Owner: ',      f'{guild.owner.name}#{guild.owner.discriminator}'],
            ['Server ID: ',         f'{guild.id}'],
            ['Categorys: ',         f'{categorys}'],
            ['Channels: ',          f'T: {textchannels} V: {voicechannels}'],
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
        botuser = ctx.bot                       # shortcut for bot. var/bot is taken
        sha = repo.head.object.hexsha           # Hash of commit that the local files are
        totalservers = len(botuser.guilds)      # List of all guilds, is a list so can len() it
        members = botuser.get_all_members()     # Reference to members, is a generator so cant len() it
        link = config['invitelink']             # Link to invite bot
        githublink = config['github']           # Github link
        prefixformat = ""                       # Formatted Prefixes

        totalmembers = 0
        for _ in members:
            totalmembers += 1

        _counter = 0 # touch this and die
        prefixes = config['prefix'] # Contains a list of prefixes
        for prefix in prefixes:
            _counter += 1
            prefixformat += prefix
            if(_counter+1 <= int(len(prefixes))):
                prefixformat += ", "

        info = [ # Makes adding easy and pretty
                ['Bot Owner: ',         f'{botuser.get_user(botuser.owner_id)}'],
                ['Global Servers: ',    f'{totalservers}'],
                ['Global Members: ',    f'{totalmembers}'],
                ['Prefix/s: ',          f'{prefixformat}'],
                ['Invite: ',            f'[Invite Bot]({link})'],
                ['Repository: ',        f'[Github]({githublink})'],
                ['Commit: ',            f'{sha}']
            ]

        embed=helpers.embed(title='Bot Statistics: ', thumbnail=botuser.user.avatar_url, fields=info)
        await ctx.send(embed=embed)

    @commands.command(
        name='ping',
        brief='ping discord api/bot',
        aliases=['p']
    )
    async def ping(self, ctx):
        embed = discord.Embed(title="Pong!", color=discord.Color.blurple())
        embed.add_field(name='API: ', value=(f'Latency: {round(self.bot.latency*1000)}ms'))
        await ctx.send(embed=embed)

    @commands.command(
        name='embed',
        brief='make an embed',
        description='args: title-None, fields[], inline-False, randcolor-True'
    )
    async def embed(self, ctx, title: str = None, fields: list = None, inline: bool = False, randcolor: bool = True):
        embed=helpers.embed(title=title, fields=fields, inline=inline, randcolor=randcolor)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(User(bot))
    # Adds user commands to the bot
    # Note: The "setup" function has to be there in every cog file
