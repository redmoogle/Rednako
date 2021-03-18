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

    @commands.command(
        name='rankings',
        brief='check your failings'
    )
    async def rank(self, ctx, page: int = 1):
        """
        Check server rankings

            Parameters:
                ctx (commands.Context): Context Reference
                page (int): Page to view
        """
        data = jsonreader.read_file(ctx.guild.id, 'xp')
        info = []
        pages = []
        rank_limit = 20 # maximum per page
        for index, member in enumerate(ctx.guild.members):
            if member.id == self.bot.user.id:
                continue
            try:
                idxp = data[str(member.id)]
                if index < rank_limit:
                    info.append([f'{member.name} ({idxp["level"]}): ', f'EXP: {idxp["xp"]}/{idxp["goal"]}'])
                else:
                    pages.append(info)
            except KeyError:
                continue # we dont care
        if not pages:
            pages.append(info)
        page = min(len(pages), page)
        await ctx.send(embed=helpers.embed(title='Server Rankings', fields=pages[1-page]))

def setup(bot):
    """does cog setup"""
    bot.add_cog(XP(bot))
