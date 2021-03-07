#pylint: disable=broad-except
"""
Owner only commands
"""

# Standard Python Modules
import sys
import subprocess
from pathlib import Path

# Discord Modules
import discord
from discord.ext import commands

# Github Module
import git

# ../modules
from modules import helpers, sql

repo = git.Repo(search_parent_directories=True)

class Owner(commands.Cog):
    """
    Various owner only commands
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        if ctx.guild:
            await ctx.message.delete()

    @commands.command(
        name='update',
        brief='update bot'
    )
    @commands.is_owner()
    async def update(self, ctx):
        """
        Updates the bot from github and restart it

            Parameters:
                ctx (commands.Context): Context Reference
        """
        local = repo.head.object.hexsha
        remote = repo.remotes.origin.fetch()[0].commit
        if str(local) != str(remote):
            info = [
                    ['Local Commit: ',  f'{local}'],
                    ['Github Commit: ', f'{remote}']
                ]

            embed=helpers.embed(title='Github Update: ', fields=info, inline=False, color=discord.Colour.gold())
            await ctx.send(embed=embed)
        gitcmd = git.cmd.Git(repo)
        gitcmd.pull()

    @commands.command(
        name='sql',
        brief='run SQL commands'
    )
    @commands.is_owner()
    async def sql(self, ctx, *, sqlinput):
        """
        Executes SQL with no filtering

            Parameters:
                ctx (commands.Context): Context Reference
                sqlinput (str): SQL string to run

            Returns:
                raw_sql (any) Anything that it might return
        """
        return await ctx.send(sql.raw_sql(sqlinput), delete_after=10)

    @commands.command(
        name='database',
        brief='Returns name and lenght of db',
        aliases=['db']
    )
    @commands.is_owner()
    async def database(self, ctx):
        """
        Shows the name of all tables and their len()'s

            Parameters:
                ctx (commands.Context): Context Reference
        """
        info = []
        for table in sql.select('sqlite_master', ['type',"'table'"], 'name'):
            rows = sql.select(table[0])
            info += [[f'Table: {table[0]}', f'Rows: {len(rows)}']]

        embed = helpers.embed(title='Databases: ', fields=info, color=discord.Colour.dark_blue())
        await ctx.send(embed=embed)

    @commands.command(
        name='cog',
        brief='adjust cogs, r-eload, u-nload, l-oad',
        aliases=['hotreload']
    )
    @commands.is_owner()
    async def reload_cog(self, ctx, adjustment: str, *, cog: str):
        """
        Messes with the cogs, reload, disable, or enable

            Parameters:
                ctx (commands.Context): Context Reference
                adjustment (str): Tells what the cog to do
                cog (str): which cog to poke
        """
        adjustment = adjustment.lower()
        _cog = f'commands.{cog}'

        try:
            if(adjustment in ['r', 'u']):
                self.bot.unload_extension(_cog)
                await ctx.send(f'**`Cog {cog} has been unloaded`**')
            if(adjustment in ['r', 'l']):
                self.bot.load_extension(_cog)
                await ctx.send(f'**`Cog {cog} has been loaded`**')
        except Exception as error:
            await ctx.send(f'**`FAILURE:`** {type(error).__name__} - {error}')

    @commands.command(
        name='reboot',
        brief='restarts bot'
    )
    @commands.is_owner()
    async def reboot(self, ctx):
        """
        Reboots the bot, mainly used for updating the core files

            Parameters:
                ctx (commands.Context): Context Reference
        """
        await ctx.send('Starting Reboot')
        await self.bot.logout()
        path = Path(__file__).parent.parent
        await subprocess.call(f'{path}/restart.sh')
        sys.exit()

    @commands.command(
        name="status",
        brief="change status of bot"
    )
    @commands.is_owner()
    async def status(self, ctx, *, newstatus):
        """
        Sets the bot status

            Parameters:
                ctx (commands.Context): Context Reference
                newstatus (str): Status to set it to
        """
        self.bot.status_str = newstatus
        await ctx.send(f"Set the new status to: {newstatus.format(self=self.bot)}")

    @commands.command(
        name='speed',
        brief='change the speed of the status'
    )
    @commands.is_owner()
    async def statspeed(self, ctx, value: int):
        """
        Changes how fast the status refreshes

            Parameters:
                ctx (commands.Context): Context Reference
                value (int): How fast to update
        """
        value = max(2, value)
        self.bot.update.change_interval(seconds=value)
        self.bot.update.restart()
        await ctx.send(f"Now updating the status every {value} seconds")

    @commands.command(
        name='vars',
        brief='Show useable vars'
    )
    @commands.is_owner()
    async def var(self, ctx):
        """
        Shows the local variables of the bot (aka super vars excluded)

            Parameters:
                ctx (commands.Context): Context Reference
        """
        info = []
        for key in self.bot.vars:
            info.append([f'self.{key}: ', self.bot.__dict__[key]])
        embed = helpers.embed(title='Useable Vars', fields=info)
        await ctx.send(embed=embed)

def setup(bot):
    """
    Setup the Owner Cog
    """
    bot.add_cog(Owner(bot))
