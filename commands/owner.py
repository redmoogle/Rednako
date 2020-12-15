from discord.ext import commands
import config
import git
import discord
import subprocess
import random
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
        if(purge > 250):
            purge = 250
            temp = await ctx.send('You can only purge upto 250 messages')
            return await temp.delete(delay=3)

        async for message in ctx.channel.history(limit=purge):
            await message.delete()

    @commands.command(
        name='ban',
        brief='fancy ban'
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, victim: discord.Member = None):
        await ctx.message.delete()
        if victim is None:
            temp = await ctx.send('You need to specify a person to ban')
            return await temp.delete(delay=3)

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
        await ctx.message.delete()
        if victim is None:
            temp = await ctx.send('You need to specify a person to kick')
            return await temp.delete(delay=3)

        funnys = [
                f'You are being exiled {victim.mention}',
                f'Stay in this hole until the end of time {victim.mention}', 
                f'I shan\'t look at you {victim.mention}',
                f'Stay away from me {victim.mention}!',
                f'{victim.mention} has failed the kneecap check'
                 ]
        random.shuffle(funnys)
        await ctx.send(str(funnys[0]))
        await victim.kick()

    @commands.command(
        name='rolecolor',
        brief='change color of a role'
    )
    @commands.has_permissions(manage_roles=True)
    async def rolecolor(self, ctx, role: discord.Role = None, color: discord.Colour = None):
        await ctx.message.delete()
        if role is None:
            temp = await ctx.send('You need to specify a role by ID or mentoning it')
            return await temp.delete(delay=3)
        if color is None:
            color = color.random()
        else:
            color = int(color, base=16)
            if not (0 <= color <= 0xFFFFFF):
                temp = await ctx.send('The color you have provided is invalid')
                return await temp.delete(delay=3)

        await role.edit(colour=color)

def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the ping command to the bot
    # Note: The "setup" function has to be there in every cog file