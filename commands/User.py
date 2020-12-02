from discord.ext import commands
import discord

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

        elif(victim): # used to ignore else
            pass

        else:
            await ctx.send("You have not mentioned anyone")
            return

        embed=discord.Embed(title=(str(victim) + " Avatar"))
        embed.set_image(url=str(victim.avatar_url))
        embed.set_author(name=("Author: " + str(ctx.author)))
        await ctx.send(embed=embed)

    @commands.command(
        name='args',
        description='prints your args',
        aliases=['send']
    )
    async def args(self, ctx, *, args):
        await ctx.send(args)


def setup(bot):
    bot.add_cog(User(bot))
    # Adds user commands to the bot
    # Note: The "setup" function has to be there in every cog file