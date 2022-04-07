"""

Rednako: Code is from https://raw.githubusercontent.com/Devoxin/lavalink.py/master/examples/music.py

This example cog demonstrates basic usage of lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.

Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""

import logging
import re
import math
import asyncio
import discord
from discord.commands import slash_command
from discord.ext import commands
import lavalink
from modules import helpers
import guildreader

class LavalinkVoiceClient(discord.VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        # ensure there exists a client already
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                    'localhost',
                    2333,
                    'youshallnotpass',
                    'us',
                    'default-node')
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
                't': 'VOICE_SERVER_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
                't': 'VOICE_STATE_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

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

url_rx = re.compile(r'https?://(?:www\.)?.+')


class Music(discord.ext.commands.Cog):
    """
    Play your weeb songs
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.lavalink = lavalink.Client(self.bot.user.id)
        self.bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'us', 'default-node')
        lavalink.add_event_hook(self.track_hook)

    async def cog_command_error(self, ctx, error):
        """
        Raised when a command errors
        """
        logging.getLogger('discord').error(error)
        if isinstance(error, commands.CommandInvokeError):
            if error is not None:
                await ctx.respond(error.original)

        if isinstance(error, ConnectionResetError):
            return

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    def djconfig(self, ctx) -> bool:
        """
        Checks the key djmode to see if djmode is on

            Parameters:
                ctx (commands.Context): Context Reference

            Returns:
                check (bool): Is DJMode disabled(True) or does user have the right role
        """
        if not ctx.guild:
            return False
        guildrole = self.bot.reader.read_file(ctx.guild.id, 'settings')['djmode']
        if guildrole is None:
            return True

        role = ctx.guild.get_role(int(guildrole))
        if role in ctx.author.roles:
            return True
        return False

    async def ensure_voice(self, ctx, connect = True):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = connect == True

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('Join a voicechannel first.')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected.')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    async def track_hook(self, event):
        """
        Event Signal for lavalink events

            Parameters:
                event (lavalink.events): The type of event that happened
        """
        # When it gets to the end of the Queue, automatically disconnect to save resources
        if isinstance(event, lavalink.events.QueueEndEvent):
            player = event.player
            sleepy = asyncio.sleep(60)
            player.store('sleeper', sleepy)
            await sleepy
            guild_id = int(event.player.guild_id)
            await player.reset_equalizer()
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

        # When a new track(song) starts it will send a message to the original channel
        if isinstance(event, lavalink.events.TrackStartEvent):
            player = event.player
            slept = player.fetch('sleeper')
            if slept:
                slept.close()
                player.store('sleeper', None)
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
            await notify_channel.send(embeds=[embed])

    @slash_command()
    async def play(self, ctx, *, query):
        """
        Plays a link or searches youtube with the provided query

            Parameters:
                ctx (commands.Context): Context Reference
                query (str): Thing or link to search/play
        """
        if not self.djconfig(ctx):
            return
        # Get the player for this guild from cache.
        await self.ensure_voice(ctx)
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from lavalink.
        results = await player.node.get_tracks(query)

        # Results could be None if lavalink returns an invalid response (non-JSON/non-200 (OK)).
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
            embed.description = f'[{track.title}]({track.uri})'
            player.add(requester=ctx.author.id, track=track)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.

        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)

        if player.is_playing:
            await ctx.respond(embeds=[embed])

        if not player.is_playing:
            await ctx.respond(":asterisk: | Started playing")
            await player.play()

    @slash_command()
    async def stop(self, ctx):
        """
        Disconnects the bot from the voicechat and clears the queue

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not self.djconfig(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # Clear the queue to ensure old tracks don't start playing
        player.queue.clear()
        # Stop the current track so lavalink consumes less resources.
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.respond(':asterisk: | Disconnected.')

    @slash_command()
    async def pause(self, ctx):
        """
        Pauses the currently playing queue

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
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
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
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
            return await ctx.respond(embeds=[embed])
        return await ctx.respond('Nothing playing')

    @slash_command()
    async def loop(self, ctx):
        """
        Loop a song or songs

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
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
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player:
            return await ctx.respond("No Player")

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
        await ctx.respond(embeds=[embed])

    @slash_command()
    async def bass(self, ctx, amount: float = 0):
        """
        Allows you to edit the bands

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                return await ctx.respond(':asterisk: | Bot is not playing any music.')

        amount = max(min(int(amount), 1), -0.25)
        await player.update_filter(lavalink.Equalizer, bands = [(0, amount),(1, amount),(2, amount),(3, amount),(4, amount),])
        await ctx.respond(f"Set bass to {amount}")

    @slash_command()
    async def mids(self, ctx, amount: float = 0):
        """
        Allows you to edit the bands

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                return await ctx.respond(':asterisk: | Bot is not playing any music.')

        amount = max(min(int(amount), 1), -0.25)
        await player.update_filter(lavalink.Equalizer, bands = [(5, amount),(6, amount),(7, amount),(8, amount),(9, amount),])
        await ctx.respond(f"Set mids to {amount}")

    @slash_command()
    async def treble(self, ctx, amount: float = 0):
        """
        Allows you to edit the bands

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                return await ctx.respond(':asterisk: | Bot is not playing any music.')

        amount = max(min(int(amount), 1), -0.25)
        await player.update_filter(lavalink.Equalizer, bands = [(10, amount),(11, amount),(12, amount),(13, amount),(14, amount),])
        await ctx.respond(f"Set treble to {amount}")

    @slash_command()
    async def reset(self, ctx):
        """
        Resets all 15 bands to default

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            await player.reset_equalizer()
            await ctx.respond('EQ has been reset')

    @slash_command()
    async def skip(self, ctx):
        """
        Skips the currently playing song

            Parameters:
                ctx (commands.Context): Context Reference
        """
        if not self.djconfig(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.is_playing:
                await ctx.respond('Skipping song')
                await player.skip()
            else:
                return await ctx.respond('Nothing Playing')
        else:
            return await ctx.respond('Nothing Playing')

    @slash_command()
    async def seek(self, ctx, timinp):
        """
        Seeks to specified timestamp
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        try:
            seekto = helpers.time_to_seconds(timinp)
        except ValueError:
            return await ctx.respond("You have provided an invalid timestamp")

        if not player:
            return await ctx.respond("No Player")

        await player.seek(seekto*1000)
        await ctx.respond(f"Seeked to {timinp}")

    @slash_command()
    async def speed(self, ctx, speed: float = 100):
        """
        Sets the playback speed
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            speed = float(speed)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.update_filter(lavalink.Timescale, speed=speed/100)
        await ctx.respond(f"Set speed to {speed}%")

    @slash_command()
    async def pitch(self, ctx, pitch: float = 100):
        """
        Sets the pitch of the player
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            pitch = float(pitch)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.update_filter(lavalink.Timescale, pitch=pitch/100)
        await ctx.respond(f"Set pitch to {pitch}%")

    @slash_command()
    async def rotation(self, ctx, rotation: float = 0):
        """
        Sets the rotation of the player
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            rotationHz = float(rotation)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.update_filter(lavalink.Rotation, rotationHz=rotationHz)
        await ctx.respond(f"Set rotation to {rotation}Hz")

    @slash_command()
    async def vibrato(self, ctx, frequency: int = 2, depth: float = 0.5):
        """
        Sets the vibrato of the player
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            frequency = max(min(int(frequency), 14), 0.001)
            depth = max(min(float(depth), 1), 0.001)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.update_filter(lavalink.Vibrato, frequency=frequency, depth=depth)
        await ctx.respond(f"Set vibrato to {frequency} with a depth of {depth}")

    @slash_command()
    async def tremolo(self, ctx, frequency: int = 2, depth: float = 0.5):
        """
        Sets the tremolo of the player
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("No Player")

        try:
            frequency = max(min(int(frequency), 14), 0.001)
            depth = max(min(float(depth), 1), 0.001)
        except ValueError:
            return await ctx.respond("Not a Number")

        await player.update_filter(lavalink.Tremolo, frequency=frequency, depth=depth)
        await ctx.respond(f"Set tremolo to {frequency} with a depth of {depth}")

    @slash_command()
    async def volume(self, ctx, vol) -> None:
        """

        Args:
            ctx: Context
            vol: Volume to set to lavalink imposes a max of 1000

        Returns:
            None
        """
        if not self.djconfig(ctx):
            return
        if not await self.ensure_voice(ctx):
            return
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        try:
            vol = int(vol)
        except ValueError:
            return await ctx.respond("Not a number")
        if not player:
            return await ctx.respond("No Player")

        vol = max(min(1000, vol), 0)
        await player.set_volume(vol)
        await ctx.respond(f"Set volume to {vol}")


def setup(bot):
    """
    Setup Music Cog
    """
    bot.add_cog(Music(bot))
