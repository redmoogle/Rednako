"""

Rednako: Code is from https://raw.githubusercontent.com/Devoxin/redlink.py/master/examples/music.py

This example cog demonstrates basic usage of redlink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.

Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""

import re
import math
import asyncio
import discord
from discord.commands import slash_command
from discord.ext import commands
from modules import redlink
from modules import helpers
import guildreader
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle


def djconfig(ctx) -> bool:
    """
    Checks the key djmode to see if djmode is on

        Parameters:
            ctx (commands.Context): Context Reference

        Returns:
            check (bool): Is DJMode disabled(True) or does user have the right role
    """
    if not ctx.guild:
        return False
    guildrole = guildreader.read_file(ctx.guild.id, 'settings')['djmode']
    if guildrole is None:
        return True

    role = ctx.guild.get_role(int(guildrole))
    if role in ctx.author.roles:
        return True
    return False

class RedlinkVoiceClient(discord.VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, bot: discord.Client, channel: discord.abc.Connectable):
        self.client = bot
        self.channel = channel
        # ensure there exists a client already
        if hasattr(self.client, 'redlink'):
            self.redlink = self.client.redlink
        else:
            self.client.redlink = redlink.Client(bot.user.id)
            self.client.redlink.add_node(
                    'localhost',
                    2333,
                    'youshallnotpass',
                    'us',
                    'default-node')
            self.redlink = self.client.redlink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        redlink_data = {
                't': 'VOICE_SERVER_UPDATE',
                'd': data
                }
        await self.redlink.voice_update_handler(redlink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        redlink_data = {
                't': 'VOICE_STATE_UPDATE',
                'd': data
                }
        await self.redlink.voice_update_handler(redlink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.redlink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.redlink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that
        # would set channel_id to None doesn't get dispatched after the 
        # disconnect
        player.channel_id = None
        self.cleanup()


class BandEditor:
    def __init__(self, ctx, player, bot):
        self.ctx = ctx
        self.player = player
        self.bands = self.player.equalizer
        self.bot = bot

        self._msg = None

        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.mainmenu())

    def eqembed(self):
        lower = -0.25
        upper = 1
        stackheight = 20

        emb = discord.Embed()
        desc = "```"
        for band, amount in enumerate(self.player.equalizer):
            percentage = (abs(lower) + amount) / (abs(upper) + abs(lower))
            filllen = stackheight - (round(percentage * stackheight))
            fill = ""
            for _ in range(filllen):
                fill += " "
            desc += f"{str(band + 1).zfill(2)}: " + ("|" * (round(percentage * stackheight))) + f"{fill}\n"

        desc += "```"
        emb.description = desc
        return emb

    async def bandmenu(self, bands):
        while True:
            comp = await self.send_or_edit(mode=2)
            result = await wait_for_component(self.bot, components=comp)
            if result.author != self.ctx.author:
                return
            if result.component_id == "up":
                for band in range(bands[0], bands[1] + 1):
                    await self.player.set_gain(band, self.player.equalizer[band] + 0.1)

            if result.component_id == "down":
                for band in range(bands[0], bands[1] + 1):
                    await self.player.set_gain(band, self.player.equalizer[band] - 0.1)

            if result.component_id == "back":
                await result.edit_origin(**self._emmsg(1))
                await self.mainmenu()
            await result.edit_origin(**self._emmsg(2))

    def _emmsg(self, mode):
        arg = {}
        if mode == 1:
            actions = create_actionrow(
                create_button(style=ButtonStyle.green, label="Bass", custom_id="bass"),
                create_button(style=ButtonStyle.green, label="Mids", custom_id="mids"),
                create_button(style=ButtonStyle.green, label="Treble", custom_id="treble"),
                create_button(style=ButtonStyle.green, label="Exit", custom_id="close")
            )

            arg["components"] = [actions]

        if mode == 2:
            actions = create_actionrow(
                create_button(style=ButtonStyle.green, label="Increase", custom_id="up"),
                create_button(style=ButtonStyle.green, label="Decrease", custom_id="down"),
                create_button(style=ButtonStyle.green, label="Back", custom_id="back"),
            )
            arg["components"] = [actions]

        arg["embed"] = self.eqembed()
        return arg

    async def send_or_edit(self, mode=1):
        arg = self._emmsg(mode)
        if not self._msg:
            self._msg = await self.ctx.respond(**arg)
        else:
            await self._msg.edit(**arg)
        return arg["components"]

    async def mainmenu(self):
        while True:
            comp = await self.send_or_edit()
            result = await wait_for_component(self.bot, components=comp)
            bandselector = 0
            if result.component_id == "bass":
                bandselector = (0, 4)
            elif result.component_id == "mids":
                bandselector = (5, 9)
            elif result.component_id == "treble":
                bandselector = (10, 14)
            elif result.component_id == "close":
                await self._msg.delete()
                break

            await result.edit_origin(**self._emmsg(2))
            await self.bandmenu(bandselector)


url_rx = re.compile(r'https?://(?:www\.)?.+')


class Music(discord.ext.commands.Cog):
    """
    Play your weeb songs
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.redlink = redlink.Client(self.bot.user.id)
        self.bot.redlink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'us', 'default-node')
        redlink.add_event_hook(self.track_hook)

    async def cog_command_error(self, ctx, error):
        """
        Raised when a command errors
        """
        if isinstance(error, commands.CommandInvokeError):
            if error is not None:
                await ctx.respond(error.original)

        if isinstance(error, ConnectionResetError):
            return

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.redlink._event_hooks.clear()

    async def ensure_voice(self, ctx, action = 0):
        """
        Additional checks that prevents the redlink code from breaking

            Parameters:
                ctx (commands.Context): Context Reference
                action (int): 0; Ignore, 1; Connect, 2; Disconnect

            Raises:
                CommandInvokeError(AdditonalDetail (str)): Error that prevents the bot from doing something
        """

        # This creates a player, OR returns the existing one, this is to make sure the player exists
        try:
            player = self.bot.redlink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        except redlink.NodeException:
            await ctx.respond('Redlink is Offline')
            return False
        except AttributeError:
            await ctx.respond('Redlink is not Initialized')
            return False

        # This is to ignore commands that shouldn't require people in the same VC
        ignored = action == 0
        if ignored:
            return True

        if(action == 2):
            await ctx.guild.voice_client.disconnect(force=True)
            return True

        # Make sure they're in a voice-chat
        if(action == 1):
            if not ctx.author.voice or not ctx.author.voice.channel:
                await ctx.respond('Join a voice-channel first!')
                return False
            if (not player.is_playing) and (not player.paused):
                player.store('channel', ctx.channel.id)
                await ctx.author.voice.channel.connect(cls=RedlinkVoiceClient)
                return True
            if player.paused:
                await ctx.respond('Currently playing')
                return False
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.respond('You need to be in my voicechannel.')
                return False

        return True

    async def track_hook(self, event):
        """
        Event Signal for redlink events

            Parameters:
                event (redlink.events): The type of event that happened
        """
        # When it gets to the end of the Queue, automatically disconnect to save resources
        if isinstance(event, redlink.events.QueueEndEvent):
            player = event.player
            guild_id = int(event.player.guild_id)
            await player.reset_equalizer()
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

        # When a new track(song) starts it will send a message to the original channel
        if isinstance(event, redlink.events.TrackStartEvent):
            player = event.player
            notify_channel = player.fetch("channel")
            notify_channel = self.bot.get_channel(notify_channel)
            vidthumbnail = f"https://img.youtube.com/vi/{player.current.identifier}/mqdefault.jpg"
            info = [
                ['Song: ', f'[{player.current.title}]({player.current.uri})'],
                ['Duration: ', f'{helpers.parse_duration(player.current.duration / 1000)[0]}'],
                ['By: ', f'{player.current.author}'],
                ['Requested By: ', f'<@{player.current.requester}>']
            ]
            embed = helpers.embed(
                description=f'```css\n{player.current.title}\n```',
                title='Now Playing: ',
                thumbnail=vidthumbnail,
                fields=info
            )
            await notify_channel.send(embed=embed)

    @slash_command()
    @commands.check(djconfig)
    async def play(self, ctx, *, query):
        """
        Plays a link or searches youtube with the provided query

            Parameters:
                ctx (commands.Context): Context Reference
                query (str): Thing or link to search/play
        """
        # Get the player for this guild from cache.
        if not await self.ensure_voice(ctx, action = 1):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)

        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can redlink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from redlink.
        results = await player.node.get_tracks(query)

        # Results could be None if redlink returns an invalid response (non-JSON/non-200 (OK)).
        # Alternatively, results['tracks'] could be an empty array if the query yielded no tracks.
        if not results or not results['tracks']:
            return await ctx.respond(helpers.embed("Nothing Found!"))

        embed = discord.Embed(color=discord.Color.blurple())

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist Enqueued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            embed.title = 'Track Enqueued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            # You can attach additional information to audiotracks through kwargs, however this involves
            # constructing the AudioTrack class yourself.
            track = redlink.models.AudioTrack(track, ctx.author.id)
            player.add(requester=ctx.author.id, track=track)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.

        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)

        if player.is_playing:
            await ctx.respond(embed=embed)

        if not player.is_playing:
            await ctx.respond(":asterisk: | Started playing")
            await player.play()

    @slash_command()
    @commands.check(djconfig)
    async def stop(self, ctx):
        """
        Disconnects the bot from the voicechat and clears the queue

            Parameters:
                ctx (commands.Context): Context Reference
        """
        player = self.bot.redlink.player_manager.get(ctx.guild.id)

        # Clear the queue to ensure old tracks don't start playing
        player.queue.clear()
        # Stop the current track so redlink consumes less resources.
        await player.stop()
        if not await self.ensure_voice(ctx, action = 2):
            return
        await ctx.respond(':asterisk: | Disconnected.')

    @slash_command()
    @commands.check(djconfig)
    async def pause(self, ctx):
        """
        Pauses the currently playing queue

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)
        if player.current is None:
            await ctx.respond(':asterisk: | Bot is not playing any music.')

        if player.paused:
            await ctx.respond(':asterisk: | Bot has been unpaused')
            await player.pause(False)
        elif not player.paused:
            await ctx.respond(':asterisk: | Bot has been paused')
            await player.pause()

    @slash_command()
    async def current(self, ctx):
        """
        Shows the currently playing song

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)
        if player.current:
            duration, fill = helpers.parse_duration(player.current.duration/1000)
            current = helpers.parse_duration(player.position/1000, fill)[0]
            vidthumbnail = f"https://img.youtube.com/vi/{player.current.identifier}/mqdefault.jpg"
            info = [
                ['Song: ', f'[{player.current.title}]({player.current.uri})'],
                ['Duration: ', f'{current}/{duration}'],
                ['By: ', f'{player.current.author}'],
                ['Requested By: ', f'<@{player.current.requester}>']
            ]
            embed = helpers.embed(
                title='Now Playing: ',
                description=f'```css\n{player.current.title}\n```',
                thumbnail=vidthumbnail,
                fields=info
            )
            return await ctx.respond(embed=embed)
        return await ctx.respond('Nothing playing')

    @slash_command()
    @commands.check(djconfig)
    async def loop(self, ctx):
        """
        Loop a song or songs

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                return await ctx.respond(':asterisk: | Bot is not playing any music.')

        repeating = player.repeat
        if repeating:
            await ctx.respond(':asterisk: | Stopped Looping.')
        else:
            await ctx.respond(':asterisk: | Now Looping.')
        player.repeat = not repeating

    @slash_command()
    async def queue(self, ctx, page: int = 1):
        """
        Iterates over the queue and sends a embed of queued tracks

            Parameters:
                ctx (commands.Context): Context Reference
                page (int): Page of the queue to look up (10 per page)
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)

        # player.current is a track but we want it to be a list with that track
        playerqueue = []
        if player.current:  # Funny bug where I forgot to check if it's a NoneType
            playerqueue = [player.current]
        # Add the rest of the queue on it
        playerqueue += player.queue
        # Formatting
        queue_list = ''
        # How many songs to display per page
        items_per_page = 10
        # Round up how many pages to make
        pages = math.ceil(len(playerqueue) / items_per_page)
        # Where to start the index to print the page
        start = (page - 1) * items_per_page
        # End of that page
        end = start + items_per_page

        # Make sure they don't pull up a 'invalid' page
        if page > pages:
            return await ctx.respond('Theres nothing on that page')

        for index, track in enumerate(playerqueue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri}) |' \
                          f' {helpers.parse_duration(track.duration / 1000)[0]}\n'

        embed = discord.Embed(colour=discord.Color.blurple(),
                              description=f'**{len(playerqueue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.respond(embed=embed)

    @slash_command()
    @commands.check(djconfig)
    async def eq(self, ctx):
        """
        Allows you to edit the bands

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                return await ctx.respond(':asterisk: | Bot is not playing any music.')

        BandEditor(ctx, player, self.bot)

    @slash_command()
    @commands.check(djconfig)
    async def reset(self, ctx):
        """
        Resets all 15 bands to default

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)
        if player:
            await player.reset_equalizer()
            await ctx.respond('EQ has been reset')

    @slash_command()
    @commands.check(djconfig)
    async def skip(self, ctx):
        """
        Skips the currently playing song

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)
        if player:
            if player.is_playing:
                await ctx.respond('Skipping song')
                await player.skip()
            else:
                return await ctx.respond('Nothing Playing')
        else:
            return await ctx.respond('Nothing Playing')

    @slash_command()
    @commands.check(djconfig)
    async def seek(self, ctx, timinp):
        """
        Seeks to specified timestamp
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)
        try:
            seekto = helpers.time_to_seconds(timinp)
        except ValueError:
            return await ctx.respond("You have provided an invalid timestamp")

        if not player:
            return await ctx.respond("No Player")

        await player.seek(seekto*1000)
        await ctx.respond(f"Seeked to {timinp}")

    @slash_command()
    @commands.check(djconfig)
    async def speed(self, ctx, speed: float = 100):
        """
        Sets the playback speed
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            speed = float(speed)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.set_speed(speed/100)
        await ctx.respond(f"Set speed to {speed}%")

    @slash_command()
    @commands.check(djconfig)
    async def pitch(self, ctx, pitch: float = 100):
        """
        Sets the pitch of the player
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            pitch = float(pitch)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.set_pitch(pitch/100)
        await ctx.respond(f"Set pitch to {pitch}%")

    @slash_command()
    @commands.check(djconfig)
    async def rotation(self, ctx, rotation: float = 0):
        """
        Sets the rotation of the player
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            rotation = float(rotation)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.set_rotation(rotation)
        await ctx.respond(f"Set rotation to {rotation}Hz")

    @slash_command()
    @commands.check(djconfig)
    async def vibrato(self, ctx, frequency: int = 2, depth: float = 0.5):
        """
        Sets the vibrato of the player
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            frequency = max(min(int(frequency), 14), 0.001)
            depth = max(min(float(depth), 1), 0.001)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.set_vibrato(frequency, depth)
        await ctx.respond(f"Set vibrato to {frequency} with a depth of {depth}")

    @slash_command()
    @commands.check(djconfig)
    async def tremolo(self, ctx, frequency: int = 2, depth: float = 0.5):
        """
        Sets the tremolo of the player
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            frequency = max(min(int(frequency), 14), 0.001)
            depth = max(min(float(depth), 1), 0.001)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.set_tremolo(frequency, depth)
        await ctx.respond(f"Set tremolo to {frequency} with a depth of {depth}")

    @slash_command()
    @commands.check(djconfig)
    async def volume(self, ctx, vol) -> None:
        """

        Args:
            ctx: Context
            vol: Volume to set to redlink imposes a max of 1000

        Returns:
            None
        """
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.redlink.player_manager.get(ctx.guild.id)
        try:
            vol = int(vol)
        except ValueError:
            return await ctx.respond("Not a number")
        if not player:
            return await ctx.respond("No Player")

        vol = max(min(5, vol), 0)
        await player.set_volume(vol)
        await ctx.respond(f"Set volume to {vol}")


def setup(bot):
    """
    Setup Music Cog
    """
    bot.add_cog(Music(bot))
