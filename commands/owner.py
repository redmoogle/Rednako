"""
Owner only commands
"""
import sys
import subprocess
from pathlib import Path
import discord
from discord.ext import commands
import git
from modules import helpers

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

            embed = helpers.embed(title='Github Update: ', fields=info, inline=False, color=discord.Colour.gold())
            await ctx.send(embed=embed)
        gitcmd = git.cmd.Git(repo)
        gitcmd.pull()

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
        subprocess.call(f'{path}/restart.sh')
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
        brief='Show usable vars'
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
        embed = helpers.embed(title='Usable Vars', fields=info)
        await ctx.send(embed=embed)


def setup(bot):
    """
    Setup the Owner Cog
    """
    bot.add_cog(Owner(bot))
