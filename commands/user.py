"""
Random commands for the user
"""
import asyncio
import config
import discord
import git
from discord.commands import slash_command
from modules import helpers, animal
import guildreader
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component

config = config.Config('./config/bot.cfg')
repo = git.Repo(search_parent_directories=True)


def grab_animal(_animal: str = None) -> str:
    """
    Validates that the animal is correct then grabs image

        Parameters:
            _animal: Name of a animal to grab

        Returns:
            url: Image URL
    """
    if not _animal:
        return animal.Animals(None).fact()
    if _animal not in ["cat", "dog", "koala", "fox", "bird", "red_panda", "panda", "racoon", "kangaroo"]:
        return None

    return animal.Animals(_animal).fact()  # Grabs image


class User(discord.ext.commands.Cog):
    """
    User Commands
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        if ctx.guild:
            await ctx.message.delete()

    @slash_command()
    async def serverinfo(self, ctx):
        """
        Embeds info about the guild it's ran in

            Parameters:
                ctx (commands.Context): Context Reference
        """
        guild = ctx.guild                           # grab guild
        textchannels = len(guild.text_channels)     # all text channels
        voicechannels = len(guild.voice_channels)   # all voice channels
        categories = len(guild.categories)          # all categories
        roles = len(guild.roles)                    # all roles
        members = len(guild.members)                # all members

        prefix = guildreader.read_file(ctx.guild.id, 'settings')['prefix']

        info = [  # Makes adding easy and pretty
            ['Server Owner: ',      f'{guild.owner.name}#{guild.owner.discriminator}'],
            ['Server ID: ',         f'{guild.id}'],
            ['Categories: ',        f'{categories}'],
            ['Channels: ',          f'T: {textchannels} V: {voicechannels}'],
            ['Prefix: ',            f'{prefix}'],
            ['Roles: ',             f'{roles}'],
            ['Members: ',           f'{members}']
        ]

        await ctx.respond(embed=helpers.embed(title=guild.name, thumbnail=guild.icon_url, fields=info))

    @slash_command()
    async def info(self, ctx):
        """
        Embeds info about the bot

            Parameters:
                ctx (commands.Context): Context Reference
        """
        link = config['invitelink']             # Link to invite bot
        githublink = config['github']           # Github link

        info = [  # Makes adding easy and pretty
                ['Bot Owner: ',         f'{self.bot.get_user(self.bot.owner_id)}'],
                ['Global Servers: ',    f'{self.bot.servers}'],
                ['Global Members: ',    f'{self.bot.members}'],
                ['Invite: ',            f'[Invite Bot]({link})'],
                ['Repository: ',        f'[Github]({githublink})'],
                ['Commit: ',            f'{repo.head.object.hexsha}']
            ]

        embed = helpers.embed(
            title='Bot Statistics: ',
            thumbnail=self.bot.user.avatar_url,
            fields=info
        )
        await ctx.respond(embed=embed)

    @slash_command()
    async def ping(self, ctx):
        """
        Pangs discord API and waits for heartbeat

            Parameters:
                ctx (commands.Context): Context Reference
        """
        embed = discord.Embed(title="Pong!", color=discord.Color.blurple())
        embed.add_field(name='API: ', value=f'Latency: {round(self.bot.latency*1000)}ms')
        await ctx.respond(embed=embed)

    @slash_command()
    async def wordcounts(self, ctx, user: discord.Member = None):
        counters = guildreader.read_file(ctx.guild.id, 'wordcount')
        info = []
        if not user:
            user = ctx.author

        for key in counters:
            # Get User counts
            try:
                info.append([f'{key.title()}: ', counters[key][str(user.id)]])
            except KeyError:
                continue
        return await ctx.respond(embed=helpers.embed(title=f'{user} Word Counts', fields=info, inline=False))

    @slash_command()
    async def catfact(self, ctx):
        """
        Gets a random probably depressing cat fact

            Parameters:
                ctx (commands.Context): Context Reference
        """
        fact = grab_animal('cat')
        info = [
            [fact, f'Requested By: {ctx.author}']
        ]
        await ctx.respond(embed=helpers.embed(title='Cat Fact', fields=info))

    @slash_command()
    async def animalfact(self, ctx):
        """`cat`, `dog`, `koala`, `fox`, `bird`, `red_panda`, `panda`, `racoon`, `kangaroo`"""
        selection = create_actionrow(create_select(
            options=[
                create_select_option("Random", value="None"),
                create_select_option("Cat", value="cat"),
                create_select_option("Dog", value="dog"),
                create_select_option("Koala", value="koala"),
                create_select_option("Fox", value="fox"),
                create_select_option("Bird", value="bird"),
                create_select_option("Red Panda", value="red_panda"),
                create_select_option("Panda", value="panda"),
                create_select_option("Racoon", value="racoon"),
                create_select_option("Kangaroo", value="kangaroo"),
            ],
            placeholder="Select or DIE",
            min_values=1,
            max_values=1
        ))
        msg = await ctx.respond("Select an Animal...", components=[selection])
        try:
            result = await wait_for_component(self.bot, components=selection, timeout=15)
        except asyncio.TimeoutError:
            await msg.delete()
        _animal = result.selected_options[0]
        if _animal == "None":
            _animal = None
        fact = grab_animal(_animal)
        if not fact:
            return await ctx.respond(f'{_animal} does not exist')

        if not _animal:
            _name = 'Random Animal Fact'
        else:
            _name = f'Random {_animal.capitalize()} Fact'

        info = [
            [fact, f'Requested By: {ctx.author}']
        ]
        await msg.edit(content=None, embed=helpers.embed(title=_name, fields=info), components=None)

    @slash_command()
    async def words(self, ctx):
        """
        See tracked words

            Parameters:
                ctx (commands.Context): Context Reference
        """
        wordjson: dict = guildreader.read_file(ctx.guild.id, 'wordcount')
        info = []
        _tmp = ""
        for key in wordjson.keys():
            _tmp += f'{key}\n'
        info = [["Tracked: ", _tmp]]
        return await ctx.respond(embed=helpers.embed(title='Tracked Words', fields=info, inline=False))


def setup(bot):
    """
    Sets up user cog
    """
    bot.add_cog(User(bot))
