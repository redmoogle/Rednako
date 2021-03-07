#pylint: disable=unused-variable
"""
Rednako Public Discord Bot
Main Repository: https://github.com/redmoogle/Rednako
License: GPL-3.0
Make sure to set up config

Also important note. If you change default_activity
in the config make sure to update the .format in here

"""
# Standard Python Modules
import time

# Discord Modules
import discord
from discord.ext import commands, tasks
from pretty_help import PrettyHelp
from cogwatch import watch

# Config
import config

# ./modules
from modules import jsonreader, helpers

# Setting up config for open-source shenanigans
config = config.Config('./config/bot.cfg')

class Rednako(commands.Bot):
    #pylint: disable=too-many-instance-attributes
    """
    Bot class for sharding later
    """
    def __init__(self):
        # Data you can use for stuff
        # How many members can the bot see
        self.members = 0
        # How many servers can the bot see
        self.servers = 0
        # Default Prefix
        self.prefix = '=='
        # Name of the bot
        self.name = None
        # ID of the bot
        self.idnum = None
        # Uptime of the bot
        self.uptime = 0
        # Stringified Version
        self.uptime_str = ""

        # Inheritance Seperator
        # Do not put settings below this unless you dont want them to show up on vars commands
        self.vars = set(vars(self))

        # Does it update its status
        self.updatestatus = True
        # Time when the bot started
        self.starttime = time.time()
        # Current Status
        self.status_str = f'{config["default_activity"]}'
        # Parameters for bot
        super().__init__(
            command_prefix=self.get_prefix,         # Set the prefix
            description='Rednako Public Bot',       # Set a description for the bot
            owner_id=config['owner_id'],            # Your unique User ID
            case_insensitive=True,                  # Make the commands case insensitive
            intents=discord.Intents.all(),          # Entirely Optional
            help_command=PrettyHelp()               # Default help command
        )

        # Task Section
        self.update.start()
        self.gen_uptime.start()

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
            return commands.when_mentioned_or(self.prefix)(self, ctx)

        if not jsonreader.check_exist('prefix'): # File will be created shortly
            return commands.when_mentioned

        return jsonreader.read_file(ctx.guild.id, 'prefix') # Guild Specific Preset

    async def on_guild_join(self, guild):
        """
        Event signal called when the bot is added to the guild

            Parameters:
                guild (discord.Guild): Guild Object
        """
        jsonreader.write_file(guild.id, 'prefix', self.prefix)

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
            return
        await ctx.send(error)

    @tasks.loop(seconds=5)
    async def update(self):
        """
        Updates the activity status of the bot
        """
        if self.updatestatus:
            await self.wait_until_ready()
            members = self.grab_members()
            servers = self.grab_servers()
            await self.change_presence(
                activity=discord.CustomActivity(
                    name=self.status_str.format(self=self)
                )
            )

    @tasks.loop(seconds=1)
    async def gen_uptime(self):
        """
        Generates the uptime of the bot
        """
        self.uptime = round(time.time() - self.starttime)
        self.uptime_str = helpers.parse_duration(self.uptime)[0]
        return self.uptime

    @watch(path='commands', preload=True, debug=False)
    async def on_ready(self):
        """
        Stuff to do when the discord.Bot finishes doing stuff
        """
        self.name = self.user.name
        self.idnum = self.user.id
        self.grab_members()
        self.grab_servers()
        print("Finished Booting Up")
        print(f'Members: {self.members}')
        print(f'Servers: {self.servers}')
        print(f'Logged in as {self.user.name} - {self.user.id}')

bot = Rednako()
bot.run(config['token'], reconnect=True)
