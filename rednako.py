"""
Rednako Public Discord Bot
Main Repository: https://github.com/redmoogle/Rednako
License: GPL-3.0
Make sure to set up config

Also important note. If you change default_activity
in the config make sure to update the .format in here

"""
import random
import time
import discord
from cogwatch import watch
from discord.ext import commands, tasks
from pretty_help import PrettyHelp
import config
from modules import jsonreader, helpers, manager

# Setting up config for open-source shenanigans
config = config.Config('./config/bot.cfg')


class Rednako(commands.Bot):
    # pylint: disable=too-many-instance-attributes
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
        # String Version
        self.uptime_str = ""

        # Inheritance Separator
        # Do not put settings below this unless you don't want them to show up on vars commands
        self.vars = set(vars(self))

        # Does it update its status
        self.updatestatus = True
        # Time when the bot started
        self.starttime = time.time()
        # Current Status
        self.status_str = config["default_activity"]
        # Last Status
        self.status = None
        # Parameters for bot
        super().__init__(
            command_prefix=self.get_prefix,  # Set the prefix
            description='Rednako Public Bot',  # Set a description for the bot
            owner_id=config['owner_id'],  # Your unique User ID
            case_insensitive=True,  # Make the commands case insensitive
            intents=discord.Intents.all(),  # Entirely Optional
            help_command=PrettyHelp()  # Default help command
        )

        # Task Section
        self.update.start()
        self.gen_uptime.start()
        self.configs = [
            ['xp', {
                'enabled': False
            }],
            ['muted', {
                'role': None
            }],
            ["economy", {}],
            ['settings', {
                'errors': False,
                'djmode': None,
                'prefix': '='
            }]
        ]

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
        self.members = len(list(self.get_all_members()))
        return self.members

    async def get_prefix(self, message):
        """
        Called from commands.Bot to set the prefix for guilds

            Parameters:
                message (discord.Message): Message Reference

            Returns:
                Prefix (str): Prefix for that guild
        """
        if not message.guild:
            return commands.when_mentioned_or(self.prefix)(self, message)

        if not jsonreader.check_exist('settings'):  # File will be created shortly
            return commands.when_mentioned

        return jsonreader.read_file(message.guild.id, 'settings')['prefix']  # Guild Specific Preset

    async def on_guild_join(self, guild):
        """
        Event signal called when the bot is added to the guild

            Parameters:
                guild (discord.Guild): Guild Object
        """
        for jsonfile in self.configs:
            if not jsonreader.read_file(guild.id, jsonfile[0]):
                jsonreader.write_file(guild.id, jsonfile[0], jsonfile[1])

    async def on_guild_remove(self, guild):
        """
        Event signal called when the bot is removed from the guild

            Parameters:
                guild (discord.Guild): Guild Object
        """
        for jsonfile in self.configs:
            jsonreader.remove(guild.id, jsonfile[0])

    async def on_message(self, message):
        """
        Event signal called when the bot sees a message

            Parameters:
                message (discord.Message): Message Reference
        """
        if self.user.id == message.author.id:  # Bad idea to not make the bot ignore itself
            return
        await self.process_commands(message)  # otherwise it wont respond
        data = jsonreader.read_file(message.guild.id, 'xp')  # Get xp data for the guild
        if data['enabled']:  # this is off by default because other funny exp bots
            try:  # we don't make the data until it is needed. bad idea? Maybe.
                idxp = data[str(message.author.id)]  # Authors EXP Data {xp, goal, level, last_used}
                if time.time() < idxp['last_used'] + 300:  # Five minute wait period
                    return
                idxp['xp'] += random.randint(1, 10)  # RNG for the fun of it
                idxp['last_used'] = time.time()  # Reset clock
                if idxp['xp'] >= idxp['goal']:
                    idxp['level'] += 1  # Increment level
                    idxp['goal'] = 20 + idxp['level'] * 25  # gotta have challenge
                    await message.reply(
                        f"Congratulations, {message.author.mention}! you have reached level {idxp['level']}")
                data[str(message.author.id)] = idxp  # Rewrite modified data
            except KeyError:
                data[str(message.author.id)] = {
                    'xp': 0,
                    'goal': 20,
                    'level': 0,
                    'last_used': time.time()
                }
            jsonreader.write_file(message.guild.id, 'xp', data)

    async def on_command_error(self, context, exception):
        """
        Event signal called when a command errors out

            Parameters:
                context (commands.Context): Context Reference
                exception (Exception): Error that happened
        """
        if not jsonreader.read_file(context.guild.id, 'settings')['errors']:
            return
        if isinstance(exception, commands.CommandNotFound):
            return await context.send(f"{context.author.mention}, command \'{context.invoked_with}\' not found!")
        if isinstance(exception, commands.CheckFailure):
            return  # Very annoying error, it just says the check failed
        await context.send(f'{type(exception)}: {exception}')

    @tasks.loop(seconds=5)
    async def update(self):
        """
        Updates the activity status of the bot
        """
        if self.updatestatus:
            await self.wait_until_ready()
            self.grab_members()
            self.grab_servers()
            self.status = self.status_str.format(self=self)
            await self.change_presence(
                activity=discord.Activity(name=self.status_str.format(self=self), type=2)
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
        self.grab_servers()
        print("Finished Booting Up")
        print(f'Members: {self.members}')
        print(f'Servers: {self.servers}')
        print(f'Logged in as {self.user.name} - {self.user.id}')
        manager.opendash(self)


bot = Rednako()
bot.run(config['token'], reconnect=True)
