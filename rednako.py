"""
Rednako Public Discord Bot
Main Repository: https://github.com/redmoogle/Rednako
License: GPL-3.0
Make sure to set up config

Also important note. If you change default_activity
in the config make sure to update the .format in here

"""
# Discord Modules
import discord
from discord.ext import commands, tasks
from pretty_help import PrettyHelp
from cogwatch import watch

# Config
import config

# ./modules
from modules import jsonreader

# Setting up config for open-source shenanigans
config = config.Config('./config/bot.cfg')
DEFAULTPREFIX = '=='

class Rednako(commands.Bot):
    """
    Bot class for sharding later
    """
    def __init__(self):
        self.members = 0
        self.servers = 0
        self.updatestatus = True
        super().__init__(
            command_prefix=self.get_prefix,         # Set the prefix
            description='Rednako Public Bot',       # Set a description for the bot
            owner_id=config['owner_id'],            # Your unique User ID
            case_insensitive=True,                  # Make the commands case insensitive
            intents=discord.Intents.all(),          # Entirely Optional
            help_command=PrettyHelp()               # Default help command
        )
        self.update.start()

    def grab_servers(self):
        """
        Grabs all the servers the bot can see

            Returns:
                servers (int): Servers the bot found
        """
        self.servers = len(self.guilds)
        return self.servers

    def grab_members(self):
        """
        Grabs all the members the bot can see

            Returns:
                members (int): Members the bot found
        """
        _members = 0
        for _ in self.get_all_members():
            _members += 1
        self.members = _members
        return self.members

    async def get_prefix(self, ctx):
        #pylint: disable=arguments-differ
        # the arguments dont actually differ, pylint is just dumb
        """
        Called from commands.Bot to set the prefix for guilds

            Parameters:
                ctx (commands.Context): Context Reference

            Returns:
                Prefix (str): Prefix for that guild
        """
        if not ctx.guild:
            return commands.when_mentioned_or(DEFAULTPREFIX)(self, ctx)

        if not jsonreader.check_exist('prefix'): # File will be created shortly
            return commands.when_mentioned

        return jsonreader.read_file(ctx.guild.id, 'prefix') # Guild Specific Preset

    async def on_guild_join(self, guild):
        """
        Event signal called when the bot is added to the guild

            Parameters:
                guild (discord.Guild): Guild Object
        """
        jsonreader.write_file(guild.id, 'prefix', DEFAULTPREFIX)

    async def on_guild_remove(self, guild):
        """
        Event signal called when the bot is removed from the guild

            Parameters:
                guild (discord.Guild): Guild Object
        """
        jsonreader.remove(guild.id, 'prefix')

    async def on_command_error(self, ctx, error):
        #pylint: disable=arguments-differ
        # the arguments dont actually differ, pylint is just dumb
        """
        Event signal called when a command errors out

            Parameters:
                ctx (commands.Context): Context Reference
                error (Exception): Error that happened
        """
        if isinstance(error, commands.CommandNotFound):
            if jsonreader.read_file(ctx.guild.id, 'errors'):
                return await ctx.send(f"{ctx.author.mention}, command \'{ctx.invoked_with}\' not found!")

    @tasks.loop(seconds=90)
    async def update(self):
        """
        Updates the activity status of the bot
        """
        if self.updatestatus:
            await self.wait_until_ready()
            members = self.grab_members()
            servers = self.grab_servers()
            await self.change_presence(
                activity=discord.Game(
                    name=(config['default_activity']).format(members, servers)
                    )
                )

    @watch(path='commands', preload=True, debug=False)
    async def on_ready(self):
        """
        Stuff to do when the discord.Bot finishes doing stuff
        """
        self.grab_members()
        self.grab_servers()
        print("Finished Booting Up")
        print(f'Members: {self.members}')
        print(f'Servers: {self.servers}')
        print(f'Logged in as {self.user.name} - {self.user.id}')

bot = Rednako()
bot.run(config['token'], reconnect=True)
