from discord.ext import commands
import config
import git
import discord
import subprocess
config = config.Config('./config.cfg')
repo = git.Repo(search_parent_directories=True)

async def repoembed():
    """
    returns a embed object of current repository commits
    """
    sha = repo.head.object.hexsha
    remotesha = repo.remotes.origin.fetch()[0].commit
    embed=discord.Embed(title="Github Update Request")
    embed.add_field(name="Current Commit: ", value=str(sha), inline=False)
    embed.add_field(name="Remote Commit: ", value=str(remotesha), inline=False)
    return embed

def isOwner(ctx):
    owner = config['owner_id']
    if(ctx.author.id == int(owner)):
        return True
    return False

# New - The Cog class must extend the commands.Cog class
class Owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name='update',
        brief='update bot'
    )
    @commands.check(isOwner)
    async def update(self, ctx):
        sha = repo.head.object.hexsha
        remotesha = repo.remotes.origin.fetch()[0].commit
        print(f'Local Commit: {sha} | Remote Commit: {remotesha}')
        if(str(sha) != str(remotesha))
            embed = await repoembed()
            await ctx.send(embed=embed)
            subprocess.call(['bash', '/home/dakotamew/Rednako/commands/restart.sh'])
            await self.bot.logout()
            exit()

def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the ping command to the bot
    # Note: The "setup" function has to be there in every cog file