from discord.ext import commands
import discord
import config
import random
import git
config = config.Config('./config.cfg')
repo = git.Repo(search_parent_directories=True)

# New - The Cog class must extend the commands.Cog class
class User(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    # Define a new command
    @commands.command(
        name='avatar',
        description='Show user avatar',
        aliases=['avtr']
    )
    async def avatar(self, ctx: commands.Context, victim: discord.Member = None):
        # grabs their avatar and embeds it
        if victim is None:
            victim = ctx.author

        embed=discord.Embed(title=(str(victim) + " Avatar"))
        embed.set_image(url=str(victim.avatar_url))
        embed.set_author(name=("Author: " + str(ctx.author)))
        await ctx.send(embed=embed)

    @commands.command(
        name='args',
        description='prints your args',
        aliases=['send', 'say']
    )
    async def args(self, ctx, *, args):
        await ctx.send(args)

    @commands.command(
        name='serverinfo',
        description='prints info about there server your in',
        aliases=['si']
    )
    async def serverinfo(self, ctx):
        guild = ctx.guild
        textchannels = 0 # all text channels
        voicechannels = 0 # all voice channels
        categorys = 0 # all categorys
        roles = 0 # all roles
        members = 0 # all members
        guildid = guild.id # ID of guild
        guildowner = guild.owner # Guild Owner
        iconurl = guild.icon_url # Guild Icon
        name = guild.name # Name of guild

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

        embed=discord.Embed(title=str(name))
        embed.set_thumbnail(url=iconurl)
        embed.color = random.randint(0, 0xffffff)
        embed.add_field(name="Owner: ", value=str(guildowner.name+'#'+guildowner.discriminator), inline=False)
        embed.add_field(name="Server ID: ", value=str(guildid), inline=False)
        embed.add_field(name="Total Channels: ", value=str("Text: " + str(textchannels) + " Voice: " + str(voicechannels)), inline=False)
        embed.add_field(name="Total Categorys: ", value=str(categorys), inline=False)
        embed.add_field(name="Total Roles: ", value=str(roles), inline=False)
        embed.add_field(name="Total Members: ", value=str(members), inline=False)

        await ctx.send(embed=embed)

    @commands.command(
        name='info',
        description='botinfo',
        aliases=['globalinfo']
    )
    async def info(self, ctx):
        totalmembers = 0
        # Get all servers
        sha = repo.head.object.hexsha
        totalservers = ctx.bot.guilds
        members = ctx.bot.get_all_members()
        link = config['invitelink']
        ownerid = ctx.bot.get_user(config['owner_id'])
        prefixes = config['prefix']
        boturl = ctx.bot.user.avatar_url
        githublink = config['github']
        prefixformat = "" # Formatted Prefixes
        _counter = 0
        for _ in members:
            totalmembers += 1

        for prefix in prefixes:
            _counter += 1
            prefixformat += prefix
            if(_counter+1 <= int(len(prefixes))):
                prefixformat += ", "

        embed=discord.Embed(title="Global Statistics")
        embed.set_thumbnail(url=boturl)
        embed.color = random.randint(0, 0xffffff)
        embed.add_field(name="Bot Owner: ", value=str(ownerid), inline=False)
        embed.add_field(name="Global Servers: ", value=str(len(totalservers)), inline=False)
        embed.add_field(name="Global Members: ", value=str(totalmembers), inline=False)
        embed.add_field(name="Prefixes: ", value=str(prefixformat), inline=False)
        embed.add_field(name="Invite Link: ", value=str(link), inline=False)
        embed.add_field(name="Github Link: ", value=str(githublink), inline=False)
        embed.add_field(name="Current Commit: ", value=str(sha), inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(User(bot))
    # Adds user commands to the bot
    # Note: The "setup" function has to be there in every cog file
