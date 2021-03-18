"""
Handles various EXP things
"""

# Discord Modules
from discord.ext import commands

# ../modules
from modules import helpers, jsonreader

class XP(commands.Cog):
    """
    XP Cog
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='exp',
        brief='check EXP'
    )
    async def exp(self, ctx):
        """
        Checks how much EXP you have

            Parameters:
                ctx (commands.Context): Context Reference
        """
        data = jsonreader.read_file(ctx.guild.id, 'xp')
        try:
            idxp = data[str(ctx.author.id)]
            exp = idxp['xp']
            goal = idxp['goal']
            level = idxp['level']
        except KeyError:
            return await ctx.send('Silent Hills')

        info = [
            [f'Level: {level} ', f'EXP: {exp}/{goal}']
        ]
        embed=helpers.embed(title=f'{ctx.author.name}\'s XP', image=ctx.author.avatar_url, fields=info)
        return await ctx.send(embed=embed)

def setup(bot):
    """does cog setup"""
    bot.add_cog(XP(bot))
