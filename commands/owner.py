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
        await ctx.message.delete()
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
        await ctx.message.delete()
        if(purge > 500):
            purge = 500
            temp = await ctx.send('You can only purge upto 500 messages')
            temp.delete(delete_after=3)
        counter = 0
        for message in ctx.channel.history(limit = 500):
            if(counter >= purge): # no need to keep processing
                break
            await message.delete()
            counter += 1

def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the ping command to the bot
    # Note: The "setup" function has to be there in every cog file