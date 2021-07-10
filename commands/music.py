"""

Rednako: Code is from https://raw.githubusercontent.com/Devoxin/Lavalink.py/master/examples/music.py

This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.

Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""

import re
import math
import time
import asyncio
import discord
from discord.ext import commands
import lavalink
from modules import helpers
import guildreader
from discord_slash import cog_ext
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component

import logging


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
            result
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
            self._msg = await self.ctx.send(**arg)
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


class Music(commands.Cog):
    """
    Play your weeb songs
    """

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            self.bot.lavalink = lavalink.Client(self.bot.user.id)
            self.bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'us', 'default-node')
            self.bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        lavalink.add_event_hook(self.track_hook)

    async def cog_command_error(self, ctx, error):
        """
        Raised when a command errors
        """
        if isinstance(error, commands.CommandInvokeError):
            if error is not None:
                await ctx.send(error.original)

        if isinstance(error, ConnectionResetError):
            return

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """
        Cog Signal called before invoking a command in this cog

            Parameters:
                ctx (commands.Context): Context Reference

            Returns:
                runnable (bool): Can the command run
        """
        await self.bot.wait_until_ready()
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            return await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, ctx):
        """
        Additional checks that prevents the lavalink code from breaking

            Parameters:
                ctx (commands.Context): Context Reference

            Raises:
                CommandInvokeError(AdditonalDetail (str)): Error that prevents the bot from doing something
        """

        # This creates a player, OR returns the existing one, this is to make sure the player exists
        try:
            if self.bot.lavaprocess and not self.bot.lavalink:
                self.bot.lavalink = lavalink.Client(self.bot.user.id)
                self.bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'us', 'default-node')
                self.bot.add_listener(self.bot.lavalink.voice_update_handler, 'on_socket_response')

            player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        except lavalink.NodeException:
            await ctx.send('Lavalink is still booting up')
            return False
        except AttributeError:
            await ctx.send('Lavalink is currently not online')
            return False

        # Should_connect is used for commands that start playback ~~aka 1 command~~
        should_connect = ctx.command in ('play', 'p')
        # This is to ignore commands that shouldn't require people in the same VC
        ignored = ctx.command in ('queue', 'np', 'current', 'reset')

        if ignored:
            return True

        # Make sure they're in a voice-chat
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('Join a voice-channel first!')
            # Raise a fake error to make the command halt
            return False

        if not player.is_connected:
            if not should_connect:
                await ctx.send('Player is not connected')
                return False

            if (not player.is_playing) and (not player.paused):
                await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)
            else:
                if player.paused:
                    await ctx.send('Currently playing')
                    return False
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.send('You need to be in my voicechannel.')
                return False

        return True

    async def track_hook(self, event):
        """
        Event Signal for lavalink events

            Parameters:
                event (lavalink.events): The type of event that happened
        """
        # When it gets to the end of the Queue, automatically disconnect to save resources
        if isinstance(event, lavalink.events.QueueEndEvent):
            player = event.player
            guild_id = int(event.player.guild_id)
            await player.reset_equalizer()
            await self.connect_to(guild_id, None)

        # When a new track(song) starts it will send a message to the original channel
        if isinstance(event, lavalink.events.TrackStartEvent):
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

    async def connect_to(self, guild_id: int, channel_id):
        """
        Connects to a voicechannel via websocket

            Parameters:
                guild_id (int): ID of the guild to connect to
                channel_id (int): ID of the channel in the guild to connect to
        """
        websoc = self.bot._connection._get_websocket(guild_id)
        await websoc.voice_state(str(guild_id), channel_id)
        # The above looks dirty, we could alternatively use `bot.shards[shard_id].ws` but that assumes
        # the bot instance is an AutoShardedBot.

    @cog_ext.cog_slash(
        name="play",
        description="play music."
    )
    @commands.check(djconfig)
    async def search_and_play(self, ctx, *, query):
        """
        Plays a link or searches youtube with the provided query

            Parameters:
                ctx (commands.Context): Context Reference
                query (str): Thing or link to search/play
        """
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player:
            # if for some reason the player doesnt exist, forcefully create it
            await self.ensure_voice(ctx=ctx)
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from Lavalink.
        results = await player.node.get_tracks(query)

        # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
        # Alternatively, results['tracks'] could be an empty array if the query yielded no tracks.
        if not results or not results['tracks']:
            return await ctx.send(helpers.embed("Nothing Found!"))

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
            track = lavalink.models.AudioTrack(track, ctx.author.id)
            player.add(requester=ctx.author.id, track=track)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.

        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        player.store("bands", {band: 0 for band in range(15)})

        if not player.is_playing:
            await player.play()
        return await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="stop",
        description="stops the player"
    )
    @commands.check(djconfig)
    async def disconnect(self, ctx):
        """
        Disconnects the bot from the voicechat and clears the queue

            Parameters:
                ctx (commands.Context): Context Reference
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # Clear the queue to ensure old tracks don't start playing
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.send(':asterisk: | Disconnected.')

    @cog_ext.cog_slash(
        name='pause',
        description='pauses the song'
    )
    @commands.check(djconfig)
    async def pause(self, ctx):
        """
        Pauses the currently playing queue

            Parameters:
                ctx (commands.Context): Context Reference
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.current is None:
            await ctx.send(':asterisk: | Bot is not playing any music.')

        if player.paused:
            await ctx.send(':asterisk: | Bot has been unpaused')
            await player.pause(False)
        elif not player.paused:
            await ctx.send(':asterisk: | Bot has been paused')
            await player.pause()

    @cog_ext.cog_slash(
        name="current",
        description="Shows the current playing song.",
    )
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
            return await ctx.send(embed=embed)
        return await ctx.send('Nothing playing')

    @cog_ext.cog_slash(
        name="loop",
        description="Loops a song or songs.",
    )
    @commands.check(djconfig)
    async def loop(self, ctx):
        """
        Loop a song or songs

            Parameters:
                ctx (commands.Context): Context Reference
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                return await ctx.send(':asterisk: | Bot is not playing any music.')

        repeating = player.repeat
        if repeating:
            await ctx.send(':asterisk: | Stopped Looping.')
        else:
            await ctx.send(':asterisk: | Now Looping.')
        player.repeat = not repeating

    @cog_ext.cog_slash(
        name='queue',
        description="shows the queue"
    )
    async def queue(self, ctx, page: int = 1):
        """
        Iterates over the queue and sends a embed of queued tracks

            Parameters:
                ctx (commands.Context): Context Reference
                page (int): Page of the queue to look up (10 per page)
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

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
            return await ctx.send('Theres nothing on that page')

        for index, track in enumerate(playerqueue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri}) |' \
                          f' {helpers.parse_duration(track.duration / 1000)[0]}\n'

        embed = discord.Embed(colour=discord.Color.blurple(),
                              description=f'**{len(playerqueue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='eq',
        description='*Thump* *Thump* *Thump*'
    )
    @commands.check(djconfig)
    async def eq(self, ctx):
        """
        Allows you to edit the bands

            Parameters:
                ctx (commands.Context): Context Reference
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                return await ctx.send(':asterisk: | Bot is not playing any music.')

        BandEditor(ctx, player, self.bot)

    @cog_ext.cog_slash(
        name='reset',
        description='unfuck the EQ'
    )
    @commands.check(djconfig)
    async def reset(self, ctx):
        """
        Resets all 15 bands to default

            Parameters:
                ctx (commands.Context): Context Reference
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            await player.reset_equalizer()
            await ctx.send('EQ has been reset')

    @cog_ext.cog_slash(
        name='skip',
        description='nobody likes your trash'
    )
    @commands.check(djconfig)
    async def skip(self, ctx):
        """
        Skips the currently playing song

            Parameters:
                ctx (commands.Context): Context Reference
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.is_playing:
                await ctx.send('Skipping song')
                await player.skip()
            else:
                return await ctx.send('Nothing Playing')
        else:
            return await ctx.send('Nothing Playing')

    @cog_ext.cog_slash(
        name="seek",
        description="Seeks to a duration"
    )
    @commands.check(djconfig)
    async def seek(self, ctx, timinp):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        try:
            seekto = helpers.time_to_seconds(timinp)
        except ValueError:
            return await ctx.send("You have provided an invalid timestamp")

        if not player:
            return await ctx.send("No Player")

        await player.seek(seekto*1000)
        await ctx.send(f"Seeked to {timinp}")

    @cog_ext.cog_slash(
        name="volume",
        description="sets the volume upto a max of 1000"
    )
    @commands.check(djconfig)
    async def volume(self, ctx, vol) -> None:
        """

        Args:
            ctx: Context
            vol: Volume to set to lavalink imposes a max of 1000

        Returns:
            None
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        try:
            vol = int(vol)
        except ValueError:
            return await ctx.send("Not a number")
        if not player:
            return await ctx.send("No Player")

        vol = max(min(1000, vol), 0)
        await player.set_volume(vol)
        await ctx.send(f"Set volume to {vol}")


def setup(bot):
    """
    Setup Music Cog
    """
    bot.add_cog(Music(bot))
