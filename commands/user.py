"""
Random commands for the user
"""
import config
import discord
import discordtextsanitizer as dts
import git
from discord.ext import commands
from modules import helpers, animal
import guildreader

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
    if _animal is None:
        return animal.Animals(None).fact()
    if _animal not in ["cat", "dog", "koala", "fox", "bird", "red_panda", "panda", "racoon", "kangaroo"]:
        return None

    return animal.Animals(_animal).fact()  # Grabs image


class User(commands.Cog):
    """
    User Commands
    """
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        if ctx.guild:
            await ctx.message.delete()

    @commands.command(
        name='say',
        brief='make the bot speak',
        aliases=['send', 'args']
    )
    async def args(self, ctx, *, args):
        """
        Sanitized Output from User Input

            Parameters:
                ctx (commands.Context): Context Reference
                args (str): What to send back
        """
        sanitized = dts.sanitize_mass_mentions(
            args, run_preprocess=True, users=True
        )
        await ctx.send(sanitized)

    @commands.command(
        name='serverinfo',
        brief='shows server info',
        aliases=['si']
    )
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

        await ctx.send(embed=helpers.embed(title=guild.name, thumbnail=guild.icon_url, fields=info))

    @commands.command(
        name='info',
        brief='botinfo',
        aliases=['globalinfo']
    )
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
                ['Commit: ',            f'{repo.head.object.hexsh}']
            ]

        embed = helpers.embed(
            title='Bot Statistics: ',
            thumbnail=self.bot.user.avatar_url,
            fields=info
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='ping',
        brief='ping discord api/bot'
    )
    async def ping(self, ctx):
        """
        Pangs discord API and waits for heartbeat

            Parameters:
                ctx (commands.Context): Context Reference
        """
        embed = discord.Embed(title="Pong!", color=discord.Color.blurple())
        embed.add_field(name='API: ', value=f'Latency: {round(self.bot.latency*1000)}ms')
        await ctx.send(embed=embed)

    @commands.command(
        name='catfact',
        brief='get slapped by the cat'
    )
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
        await ctx.send(embed=helpers.embed(title='Cat Fact', fields=info))

    @commands.command(
        name='animalfact'
    )
    async def animalfact(self, ctx, _animal: str = None):
        """`cat`, `dog`, `koala`, `fox`, `bird`, `red_panda`, `panda`, `racoon`, `kangaroo`"""
        fact = grab_animal(_animal)
        if not fact:
            return await ctx.send(f'{_animal} does not exist')

        if not _animal:
            _name = 'Random Animal Fact'
        else:
            _name = f'Random {_animal.capitalize()} Fact'

        info = [
            [fact, f'Requested By: {ctx.author}']
        ]

        await ctx.send(embed=helpers.embed(title=_name, fields=info))


def setup(bot):
    """
    Sets up user cog
    """
    bot.add_cog(User(bot))
