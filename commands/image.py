from discord.ext import commands
import discord
import random
import nekos

# Dont worry I can feel the disappointment from my computer
# New - The Cog class must extend the commands.Cog class
class Image(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    # Define a new command
    @commands.command(
        name='neko',
        brief='send embedded catgirl'
    )
    async def neko(self, ctx):
        embed = discord.Embed(title="Neko", color=discord.Color.blurple())
        imgtype = 'neko'
        embed.set_image(url=str(nekos.img(imgtype)))
        await ctx.send(embed=embed)

    @commands.command(
        name='kitsune',
        brief='send embedded foxgirl'
    )
    async def kitsune(self, ctx):
        embed = discord.Embed(title="Kitsune", color=discord.Color.blurple())
        imgtype = 'fox_girl'
        embed.set_image(url=str(nekos.img(imgtype)))
        await ctx.send(embed=embed)

    @commands.command(
        name='avatar',
        brief='Show user avatar',
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

def setup(bot):
    bot.add_cog(Image(bot))
    # Adds image commands to the bot
    # Note: The "setup" function has to be there in every cog file
