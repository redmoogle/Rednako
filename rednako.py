"""
Rednako Public Discord Bot
Main Repository: https://github.com/redmoogle/Rednako
License: GPL-3.0
Make sure to set up config

"""
import os
import sys
import subprocess
import logging
from pathlib import Path
import time
import discord
from discord.ext import commands, tasks
import guildreader
import config
from modules import helpers, manager

# Setting up config for open-source shenanigans
config = config.Config('./config/bot.cfg')

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def contains_word(search, instring):
    """
    Checks if string is in word
    """
    return search.lower() in instring.lower().split()

class Rednako(commands.Bot):
    # pylint: disable=too-many-instance-attributes
    """
    Bot class for sharding later
    """

    def __init__(self, start_lava = True):
        """
        start_lava(bool): Start Lavalink if needed
        """
        # Data you can use for stuff
        # How many members can the bot see
        self.members = 0
        # How many servers can the bot see
        self.servers = 0
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

        if(start_lava):
            print("Starting Lavalink")
            self.lavaprocess = subprocess.Popen(
                f"java -jar {os.path.abspath('./Lavalink.jar')}",
                stdout=subprocess.DEVNULL,
                shell=True)
            print(f"Started Lavalink: PID-{self.lavaprocess.pid}")

        # Does it update its status
        self.updatestatus = True
        # Time when the bot started
        self.starttime = time.time()
        # Current Status
        self.status_str = config["default_activity"]
        # Path of the parent dir
        self.path = Path(__file__).parent
        # Reader for files
        self.reader = guildreader.Reader("./data")
        # Parameters for bot
        super().__init__(
            command_prefix=self.get_prefix,    # Set the prefix
            description='Rednako Public Bot',  # Set a description for the bot
            owner_id=config['owner_id'],       # Your unique User ID
            case_insensitive=True,             # Make the commands case insensitive
            intents=discord.Intents.all(),     # Entirely Optional
            help_command=None                  # This is a slash bot
        )

        # List of configs setup like
        # list(
        #   list(name, value),
        #   list(name, value)
        # )
        self.configs = [
            ['settings', {
                'errors': False,
                'djmode': None,
            }],
            ['wordcount', {}]
        ]

        # Task Section
        self.update.start()
        self.gen_uptime.start()
        self.check_guilds.start()

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
        return "IEEE!"

    async def on_guild_join(self, guild):
        """
        Event signal called when the bot is added to the guild

            Parameters:
                guild (discord.Guild): Guild Object
        """
        self.reader.add_id(guild.id)
        for jsonfile in self.configs:
            self.reader.read_file(guild.id, jsonfile[0])

    async def on_guild_remove(self, guild):
        """
        Event signal called when the bot is removed from the guild

            Parameters:
                guild (discord.Guild): Guild Object
        """
        self.reader.remove_id(guild.id)
        for jsonfile in self.configs:
            self.reader.remove(guild.id, jsonfile[0])

    async def on_command_error(self, context, exception):
        """
        Event signal called when a command errors out

            Parameters:
                context (commands.Context): Context Reference
                exception (Exception): Error that happened
        """
        if isinstance(exception, commands.errors.MissingPermissions):
            return await context.send(exception.message)
        logging.getLogger('discord').error(exception)
        if not self.reader.read_file(context.guild.id, 'settings')['errors']:
            return
        if isinstance(exception, commands.CheckFailure):
            return  # Very annoying error, it just says the check failed
        await context.send(f'{type(exception)}: {exception}')

    async def on_message(self, message):
        guild = message.guild
        if message.author.id == self.id:
            return
        counters = self.reader.read_file(guild.id, 'wordcount')
        for key in counters:
            if contains_word(key, message.content):
                try:
                    counters[key][str(message.author.id)] += 1
                except KeyError:
                    counters[key][str(message.author.id)] = 1
        self.reader.write_file(guild.id, 'wordcount', counters)
        return await super().on_message(message)

    @tasks.loop(seconds=5)
    async def update(self):
        """
        Updates the activity status of the bot
        """
        if self.updatestatus:
            await self.wait_until_ready()
            self.grab_members()
            self.grab_servers()
            #self.status = self.status_str.format(self=self)
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

    @tasks.loop(minutes=30)
    async def check_guilds(self):
        """
        Make sure all guilds have their configs and trims the files
        """
        _guilds = [] # We use str instead of ints
        await self.wait_until_ready()
        for jsonfile in self.configs:
            for guild in self.guilds:
                _guilds.append(str(guild.id))
                self.reader.read_file(guild.id, jsonfile[0])

                if isinstance(jsonfile[1], dict):
                    test = self.reader.read_file(guild.id, jsonfile[0])
                    if not test:
                        continue
                    for setting in jsonfile[1]:
                        try:
                            _ = test[setting]
                        except KeyError:
                            test[setting] = jsonfile[1][setting]
                    self.reader.write_file(guild.id, jsonfile[0], test)

            raw = self.reader.dump(jsonfile[0])
            for key in raw:
                if key in self.guilds:
                    continue
                self.reader.remove(key, jsonfile[0])

    async def on_ready(self):
        """
        Stuff to do when the discord.Bot finishes doing stuff
        """
        # Both of these vars start out as None
        self.name = self.user.name
        self.idnum = self.user.id

        print("Finished Booting Up")
        print(f'Members: {self.members}')
        print(f'Servers: {self.servers}')
        print(f'Logged in as {self.user.name} - {self.user.id}')

        self.reader.update_ids(self.guilds)

        for _config in self.configs:
            self.reader.create_file(_config[0], _config[1])

        manager.opendash(self)
        await self.register_commands()

    def close_bot(self):
        """ Closes the bot, exists because of a call from a external thread. """
        subprocess.call(f'{self.path}/restart.sh')
        sys.exit()

print("""
██████╗ ███████╗██████╗ ███╗   ██╗ █████╗ ██╗  ██╗ ██████╗ 
██╔══██╗██╔════╝██╔══██╗████╗  ██║██╔══██╗██║ ██╔╝██╔═══██╗
██████╔╝█████╗  ██║  ██║██╔██╗ ██║███████║█████╔╝ ██║   ██║
██╔══██╗██╔══╝  ██║  ██║██║╚██╗██║██╔══██║██╔═██╗ ██║   ██║
██║  ██║███████╗██████╔╝██║ ╚████║██║  ██║██║  ██╗╚██████╔╝
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝                                                                                                                                                                                
""")

print("--***-------------------------------------------------***--")
print("Start Options:\n")
print("1: Start with Lavalink")
print("2: Start Without Lavalink\n")
print("--***-------------------------------------------------***--")
try:
    opt = int(input(":"))
    if opt == 1:
        bot = Rednako(start_lava = True)
    elif opt == 2:
        bot = Rednako(start_lava = False)

    bot.load_extension('commands.image')
    bot.load_extension('commands.music')
    bot.load_extension('commands.settings')
    bot.load_extension('commands.user')
    bot.run(config['token'], reconnect=True)
except ValueError:
    print("Not a valid option")