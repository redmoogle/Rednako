"""
Image commands
"""
from email.mime import image
import random
import discord
from discord.commands import slash_command
from modules import helpers
from modules import animal as animals


def grab_animal(_animal: str = None) -> str:
    """
    Validates that the animal is correct then grabs image

        Parameters:
            _animal: Name of a animal to grab

        Returns:
            url: Image URL
    """
    if not _animal:
        return animals.Animals(None).image()
    if _animal == "bird":
        _animal = "birb"  # who shitposts in their module?
    if _animal not in ["cat", "dog", "koala", "fox", "birb", "red_panda", "panda", "racoon", "kangaroo"]:
        return None

    return animals.Animals(_animal).image()  # Grabs image


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
            title = 'Random Animal Image'
            result = None
        else:
            title = f'Random {result.capitalize()} Image'

        image = grab_animal(result)

        return await interaction.response.send_message(embeds=[helpers.embed(title=title, fields=[['Requested By', interaction.user]],image=image)])


class Image(discord.ext.commands.Cog):
    """
    Commands that send images
    """
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def avatar(self, ctx, user: discord.Member = None):
        """
        Sends a persons avatar

            Parameters:
                ctx (commands.Context): Context Reference
                user (discord.Member): Person to grab avatar from
        """
        # grabs their avatar and embeds it
        if user is None:
            user = ctx.author

        await ctx.respond(embed=helpers.embed(title=f'{user}\'s Avatar', image=user.avatar_url))

    @slash_command()
    async def cat(self, ctx):
        """
        Grabs a cat... *yoink*

            Parameters:
                ctx (commands.Context): Context Reference
        """
        url = grab_animal('cat')
        randomtitles = [
            "Meow",
            "Mao",
            "Mreow",
            "Chirp",
            "Purr",
            "*Cat Noises*"
        ]
        random.shuffle(randomtitles)
        await ctx.respond(embed=helpers.embed(title=randomtitles[0], image=url))

    @slash_command()
    async def animal(self, ctx):
        return await ctx.respond("Pick a animal", view=AniModal())


def setup(bot):
    """
    Add Image Cog
    """
    bot.add_cog(Image(bot))
