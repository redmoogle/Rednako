from discord.ext import commands
import discord
import lavalink

class Equalizer(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.band_count = 15
        self.bands = [0.0 for _loop_counter in range(self.band_count)]

    async def _apply_gain(self, guild_id: int, band: int, gain: float) -> None:
        const = {
            "op": "equalizer",
            "guildId": str(guild_id),
            "bands": [{"band": band, "gain": gain}],
        }

        try:
            await lavalink.get_player(guild_id).node.send({**const})
        except (KeyError, IndexError):
            pass

    async def _apply_gains(self, guild_id: int, gains: list) -> None:
        const = {
            "op": "equalizer",
            "guildId": str(guild_id),
            "bands": [{"band": x, "gain": y} for x, y in enumerate(gains)],
        }

        try:
            await lavalink.get_player(guild_id).node.send({**const})
        except (KeyError, IndexError):
            pass

    async def visualise(self):
        block = ""
        bands = [str(band + 1).zfill(2) for band in range(self.band_count)]
        bottom = (" " * 8) + " ".join(bands)
        gains = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.25]

        for gain in gains:
            prefix = ""
            if gain > 0:
                prefix = "+"
            elif gain == 0:
                prefix = " "

            block += f"{prefix}{gain:.2f} | "

            for value in self.bands:
                if value >= gain:
                    block += "[] "
                else:
                    block += "   "

            block += "\n"

        block += bottom
        return block

    @commands.command(
        name='set-eq',
        brief='set the eq'
    )
    async def command_equalizer_set(
        self, ctx: commands.Context, band_name_or_position, band_value: float):
        """Set an eq band with a band number or name and value.

        Band positions are 1-15 and values have a range of -0.25 to 1.0.
        Band names are 25, 40, 63, 100, 160, 250, 400, 630, 1k, 1.6k, 2.5k, 4k,
        6.3k, 10k, and 16k Hz.
        Setting a band value to -0.25 nullifies it while +0.25 is double.
        """

        player = lavalink.get_player(ctx.guild.id)
        band_names = [
            "25",
            "40",
            "63",
            "100",
            "160",
            "250",
            "400",
            "630",
            "1k",
            "1.6k",
            "2.5k",
            "4k",
            "6.3k",
            "10k",
            "16k",
        ]

        eq = player.fetch("eq", Equalizer())
        bands_num = eq.band_count
        if band_value > 1:
            band_value = 1
        elif band_value <= -0.25:
            band_value = -0.25
        else:
            band_value = round(band_value, 1)

        try:
            band_number = int(band_name_or_position) - 1
        except ValueError:
            band_number = 1000

        if band_number not in range(0, bands_num) and band_name_or_position not in band_names:
            await ctx.send(embed=discord.Embed(
                title=("Invalid Band."), description=(
                    "Valid band numbers are 1-15 or the band names listed in "
                    "the help for this command."
                    )
                )
            )

        if band_name_or_position in band_names:
            band_pos = band_names.index(band_name_or_position)
            band_int = False
            eq.set_gain(int(band_pos), band_value)
            await self._apply_gain(ctx.guild.id, int(band_pos), band_value)
        else:
            band_int = True
            eq.set_gain(band_number, band_value)
            await self._apply_gain(ctx.guild.id, band_number, band_value)

        player.store("eq", eq)
        band_name = band_names[band_number] if band_int else band_name_or_position
        await ctx.send(
            content=(f'```ini\n{eq.visualise()}\n```'),
            embed=discord.Embed(
                title=("Preset Modified"),
                description=("The {band_name}Hz band has been set to {band_value}.").format(
                    band_name=band_name, band_value=band_value
                ),
            ),
        )

    @commands.command(
        name="reset-eq",
        brief='reset the eq'
        )
    async def command_equalizer_reset(self, ctx):
        """Reset the eq to 0 across all bands."""
        player = lavalink.get_player(ctx.guild.id)
        eq = player.fetch("eq", Equalizer())

        for band in range(eq.band_count):
            eq.set_gain(band, 0.0)

        await self._apply_gains(ctx.guild.id, eq.bands)
        player.store("eq", eq)
        await ctx.send(
            content=(f'```ini\n{eq.visualise()}\n```'),
            embed=discord.Embed(
                colour=await ctx.embed_colour(), title=("Equalizer values have been reset.")
            ),
        )

def setup(bot):
    bot.add_cog(Equalizer(bot))