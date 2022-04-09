"""
Random commands for the user
"""
import config
import discord
import git
from discord.commands import slash_command
from modules import helpers, animal

config = config.Config('./config/bot.cfg')
repo = git.Repo(search_parent_directories=True)


def grab_animal(_animal: str = None) -> str:
    """
    Validates that the animal is correct then grabs fact

        Parameters:
            _animal: Name of a animal to grab

        Returns:
            fact: a fact about the animal
    """
    if not _animal:
        return animal.Animals(None).fact()
    if _animal not in ["cat", "dog", "koala", "fox", "bird", "red_panda", "panda", "racoon", "kangaroo"]:
        return None

    return animal.Animals(_animal).fact()  # Grabs image


class AniModal(discord.ui.View):
    @discord.ui.select(
        min_values=1, 
        max_values=1, 
        options=[
            discord.SelectOption(label="Random", value="None", emoji="🎲"),
            discord.SelectOption(label="Cat", value="cat", emoji="🐈"),
            discord.SelectOption(label="Dog", value="dog", emoji="🐶"),
            discord.SelectOption(label="Koala", value="koala", emoji="🐨"),
            discord.SelectOption(label="Bird", value="bird", emoji="🐦"),
            discord.SelectOption(label="Fox", value="fox", emoji="🦊"),
            discord.SelectOption(label="Red Panda", value="red_panda", emoji="🔴"),
            discord.SelectOption(label="Panda", value="panda", emoji="🐼"),
            discord.SelectOption(label="Racoon", value="racoon", emoji="🦝"),
            discord.SelectOption(label="Kangaroo", value="kangaroo", emoji="🦘")
        ], 
        placeholder="Select..."
    )
    async def select_callback(self, select, interaction):
        result = select.values[0]
        if result == "None":
            title = 'Random Animal Fact'
            result = None
        else:
            title = f'Random {result.capitalize()} Fact'

        fact = grab_animal(result)

        return await interaction.response.edit_message(content=None, embeds=[helpers.embed(title=title,fields=[[fact, f'Requested By: {interaction.user}']])], view=None)


class User(discord.ext.commands.Cog):
    """
    User Commands
    """
    def __init__(self, bot):
        self.bot = bot

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

        prefix = self.bot.reader.read_file(ctx.guild.id, 'settings')['prefix']

        info = [  # Makes adding easy and pretty
            ['Server Owner: ',      f'{guild.owner.name}#{guild.owner.discriminator}'],
            ['Server ID: ',         f'{guild.id}'],
            ['Categories: ',        f'{categories}'],
            ['Channels: ',          f'T: {textchannels} V: {voicechannels}'],
            ['Prefix: ',            f'{prefix}'],
            ['Roles: ',             f'{roles}'],
            ['Members: ',           f'{members}']
        ]

        await ctx.respond(embeds=[helpers.embed(title=guild.name, thumbnail=guild.icon_url, fields=info)])

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
        await ctx.respond(embeds=[embed])

    @slash_command()
    async def ping(self, ctx):
        """
        Pangs discord API and waits for heartbeat

            Parameters:
                ctx (commands.Context): Context Reference
        """
        embed = discord.Embed(title="Pong!", color=discord.Color.blurple())
        embed.add_field(name='API: ', value=f'Latency: {round(self.bot.latency*1000)}ms')
        await ctx.respond(embeds=[embed])

    @slash_command()
    async def wordcounts(self, ctx, user: discord.Member = None):
        counters = self.bot.reader.read_file(ctx.guild.id, 'wordcount')
        info = []
        if not user:
            user = ctx.author

        for key in counters:
            # Get User counts
            try:
                info.append([f'{key.title()}: ', counters[key][str(user.id)]])
            except KeyError:
                continue
        return await ctx.respond(embeds=[helpers.embed(title=f'{user} Word Counts', fields=info, inline=False)])

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
        await ctx.respond(embeds=[helpers.embed(title='Cat Fact', fields=info)])

    @slash_command()
    async def animalfact(self, ctx):
        """Shows some facts about a requested animal"""
        await ctx.respond("Pick a animal", view=AniModal())

    @slash_command()
    async def words(self, ctx):
        """
        See tracked words

            Parameters:
                ctx (commands.Context): Context Reference
        """
        wordjson: dict = self.bot.reader.read_file(ctx.guild.id, 'wordcount')
        info = []
        _tmp = ""
        for key in wordjson.keys():
            _tmp += f'{key}\n'
        info = [["Tracked: ", _tmp]]
        return await ctx.respond(embeds=[helpers.embed(title='Tracked Words', fields=info, inline=False)])


def setup(bot):
    """
    Sets up user cog
    """
    bot.add_cog(User(bot))
