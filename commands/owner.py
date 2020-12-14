from discord.ext import commands
import config
import git
config = config.Config('./config.cfg')
repo = git.Repo(search_parent_directories=True)
remoterepo = git.Repo(config['github'])

def isOwner(ctx):
    owner = config['owner_id']
    if(ctx.author.id == int(owner)):
        return True
    return False

# New - The Cog class must extend the commands.Cog class
class Owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='update')
    @commands.check(isOwner)
    async def update(self, ctx):
        sha = repo.head.object.hexsha
        remotesha = remoterepo.head.object.hexsha
        await ctx.send(f'current commit {sha}, remote commit {remotesha}')
    
def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the ping command to the bot
    # Note: The "setup" function has to be there in every cog file