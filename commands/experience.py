"""
Handles various EXP things
"""
from discord.ext import commands
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
        rank_limit = 20  # maximum per page
        _index = 0  # Enumerate cant be used because we DO modify this
        for member in ctx.guild.members:
            if member.id == self.bot.user.id:
                continue
            try:
                idxp = data[str(member.id)]
                if _index > rank_limit:
                    pages.append(info)
                    _index = 0  # Reset Index
                    info = []  # Blank it back out
                _index += 1
                info.append([f'{member.name} ({idxp["level"]}): ', f'EXP: {idxp["xp"]}/{idxp["goal"]}'])
            except KeyError:
                continue  # we don't care
        if not pages:
            pages.append(info)
        page = min(len(pages), page)
        await ctx.send(embed=helpers.embed(title='Server Rankings', fields=pages[page-1]))

    @commands.command(
        name='grankings',
        brief='Check how bad you are against everyone',
        aliases=['grank']
    )
    async def grank(self, ctx, page: int = 1):
        info = []
        pages = []
        rank_limit = 20  # maximum per page
        _index = 0  # Enumerate cant be used because we DO modify this
        globdata = {}
        for guild in self.bot.guilds:
            guilddata = jsonreader.read_file(guild.id, 'xp')
            for member in guild.members:
                try:
                    idxp = guilddata[str(member.id)]
                    gdata = {}
                    if not str(member.id) in globdata:
                        globdata[str(member.id)] = {
                            'in': 0,
                            'levels': 0,
                            'txp': 0,
                            'avglev': 0,
                            'usr': member.name
                        }
                    gdata = globdata[str(member.id)]
                    gdata['in'] += 1
                    gdata['levels'] += idxp['level']
                    gdata['txp'] += idxp['xp']
                    gdata['avglev'] = (gdata['levels']/gdata['in'])
                    globdata[str(member.id)] = gdata
                except KeyError:
                    continue

        for key in globdata.keys():
            gdxp = globdata[key]
            if _index > rank_limit:
                pages.append(info)
                _index = 0  # Reset Index
                info = []  # Blank it back out
            _index += 1
            info.append([f'{gdxp["usr"]} ~{gdxp["avglev"]}({gdxp["levels"]}/{gdxp["in"]}): ', f'Total EXP: {gdxp["txp"]}'])

        if not pages:
            pages.append(info)
        page = min(len(pages), page)
        await ctx.send(embed=helpers.embed(title='Global Rankings', fields=pages[page-1]))


def setup(bot):
    """does cog setup"""
    bot.add_cog(XP(bot))
