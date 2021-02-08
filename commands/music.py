"""

Rednako: Code is from https://raw.githubusercontent.com/Devoxin/Lavalink.py/master/examples/music.py

This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.

Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""

# Standard Python Modules
import re
import math
import asyncio

# Discord Modules
import discord
from discord.ext import commands

# RED lavalink module
import lavalink

# ../modules
from modules import jsonreader
from modules import helpers

def djconfig(ctx):
    """
    Checks config to see if that guild has defined a DJ role
    """
    guildrole = jsonreader.read_file(ctx.bot, ctx, 'djmode', None)
    if guildrole is None:
        return True

    role = ctx.guild.get_role(int(guildrole))
    if role in ctx.author.roles:
        return True
    return False

def parse_duration(duration: int):
    """
    Parse duration into DD:HH:MM:SS
    """
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    duration = []
    if days > 0:
        duration.append(f'{round(days)}:')
    if hours > 0:
        duration.append(f'{round(hours)}:')
    if minutes > 0:
        duration.append(f'{round(minutes)}:')
    if seconds > 0:
        duration.append(f'{round(seconds)}')

    return ''.join(duration)

url_rx = re.compile(r'https?://(?:www\.)?.+')

class Music(commands.Cog):
    """
    Play your weeb songs
    """
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            self.bot.lavalink = lavalink.Client(self.bot.user.id)
            self.bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'us', 'default-node')  # Host, Port, Password, Region, Name
            self.bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        lavalink.add_event_hook(self.track_hook)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            if error is not None:
                await ctx.send(error.original)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        loop = asyncio.get_event_loop()
        loop.create_task(lavalink.close())

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        await self.bot.wait_until_ready()
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """

        # This creates a player, OR returns the existing one, this is to make sure the player exists
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        # Should_connect is used for commands that start playback ~~aka 1 command~~
        should_connect = ctx.command.name in ('play', 'p')
        # This is to ignore commands that shouldnt require people in the same VC
        ignored = ctx.command.name in ('queue', 'np', 'current')

        # Make sure they're in a voice-chat
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('Join a voice-channel first!')
            # Raise a fake error to make the command halt
            raise commands.CommandInvokeError(None)

        if not player.is_connected:
            if not should_connect:
                await ctx.send('player is not connected')
                raise commands.CommandInvokeError(None)

            if (not player.is_playing) and (not player.paused):
                await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)
            else:
                if player.paused:
                    await ctx.send('Currently playing')
                    raise commands.CommandInvokeError(None)
        else:
            if not ignored:
                if int(player.channel_id) != ctx.author.voice.channel.id:
                    await ctx.send('You need to be in my voicechannel.')
                    raise commands.CommandInvokeError(None)

    async def track_hook(self, event):
        """
        Track lavalink events
        """
        # When it gets to the end of the Queue, automatically disconnect to save resources
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

        # When a new track(song) starts it will send a message to the original channel
        if isinstance(event, lavalink.events.TrackStartEvent):
            player = event.player
            notify_channel = player.fetch("channel")
            notify_channel = self.bot.get_channel(notify_channel)
            requester = player.fetch("requestee")
            vidthumbnail = f"https://img.youtube.com/vi/{player.current.identifier}/mqdefault.jpg"
            info = [
                ['Song: ', f'[{player.current.title}]({player.current.uri})'],
                ['Duration: ', f'{parse_duration(player.current.duration/1000)}'],
                ['By: ', f'{player.current.author}'],
                ['Requested By: ', f'{requester}']
            ]
            embed=helpers.embed(
                title='Now Playing: ',
                description=f'```css\n{player.current.title}\n```',
                thumbnail=vidthumbnail,
                fields=info
                )
            await notify_channel.send(embed=embed)

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        websoc = self.bot._connection._get_websocket(guild_id)
        await websoc.voice_state(str(guild_id), channel_id)
        # The above looks dirty, we could alternatively use `bot.shards[shard_id].ws` but that assumes
        # the bot instance is an AutoShardedBot.

    @commands.command(
        name="play",
        description="play music.",
        usage="play [song]",
        aliases=['p']
    )
    @commands.check(djconfig)
    async def search_and_play(self, ctx, *, query):
        """ Searches and plays a song from a given query. """
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
        # ALternatively, resullts['tracks'] could be an empty array if the query yielded no tracks.
        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

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
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.

        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        player.store("requestee", ctx.author.mention)

        if player.is_playing:
            await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

    @commands.command(aliases=['dc', 'stop'])
    @commands.check(djconfig)
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await self.connect_to(ctx.guild.id, None)
        await ctx.send(':asterisk: | Disconnected.')

    @commands.command(
        name='pause',
        brief='pauses the song'
    )
    @commands.check(djconfig)
    async def pause(self, ctx):
        """pauses the player."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                await ctx.send(':asterisk: | Bot is not playing any music.')

        if player.paused:
            await ctx.send(':asterisk: | Bot has been unpaused')
            await player.pause(False)
        elif not player.paused:
            await ctx.send(':asterisk: | Bot has been paused')
            await player.pause()

    @commands.command(
        name="current",
        description="Shows the current playing song.",
        usage="current",
        aliases=['np']
    )
    async def current(self,ctx):
        """
        Shows whats poppin
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        requester = player.fetch("requestee")
        if player.is_playing:
            vidthumbnail = f"https://img.youtube.com/vi/{player.current.identifier}/mqdefault.jpg"
            info = [
                    ['Song: ', f'[{player.current.title}]({player.current.uri})'],
                    ['Duration: ', f'{parse_duration(player.current.duration/1000)}'],
                    ['By: ', f'{player.current.author}'],
                    ['Requested By: ', f'{requester}']
                ]
            embed=helpers.embed(
                title='Now Playing: ',
                description=f'```css\n{player.current.title}\n```',
                thumbnail=vidthumbnail,
                fields=info
            )
            return await ctx.send(embed=embed)
        return await ctx.send('Nothing playing')

    @commands.command(name='queue')
    async def queue(self, ctx, page: int = 1):
        """Shows the queue"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        player.current = [player.current]
        playerqueue += player.queue

        queue_list = ''

        items_per_page = 10
        pages = math.ceil(len(playerqueue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        for index, track in enumerate(playerqueue[start:end], start=start):
            await ctx.send(track)
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri}) | {parse_duration(track.duration/1000)}\n'

        embed = discord.Embed(colour=discord.Color.blurple(),
                            description=f'**{len(playerqueue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(
        name='bass',
        brief='blow eardrums up'
    )
    @commands.check(djconfig)
    async def bass(self, ctx, gain: int = 0):
        """increases the base."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                await ctx.send(':asterisk: | Bot is not playing any music.')

        gain = max(min(1, gain), -0.25)
        await player.set_gains((0, gain*.75),(1, gain*.75),(2, gain*.75),(3, gain),(4, gain*.75))
        if gain:
            await ctx.send(f'Bass set to {(gain+1)*100}%')
        else:
            await ctx.send('Bass set to 100%')

    @commands.command(
        name='mid',
        brief='serinity'
    )
    @commands.check(djconfig)
    async def mids(self, ctx, gain: int = 0):
        """increases the mids."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                await ctx.send(':asterisk: | Bot is not playing any music.')

        gain = max(min(1, gain), -0.25)
        await player.set_gains((5, gain*.75),(6, gain*.75),(7, gain*.75),(8, gain),(9, gain*.75))
        if gain:
            await ctx.send(f'Mids set to {(gain+1)*100}%')
        else:
            await ctx.send('Mids set to 100%')

    @commands.command(
        name='treble',
        brief='blow eardrums up'
    )
    @commands.check(djconfig)
    async def treble(self, ctx, gain: int = 0):
        """increases the treble."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                await ctx.send(':asterisk: | Bot is not playing any music.')

        gain = max(-0.25, min(1, gain))
        await player.set_gains((10, gain*.75),(11, gain*.75),(12, gain*.75),(13, gain),(14, gain*.75))
        if gain:
            await ctx.send(f'Treble set to {(gain+1)*100}%')
        else:
            await ctx.send('Treble set to 100%')

    @commands.command(
        name='reset',
        brief='unfuck the EQ'
    )
    @commands.check(djconfig)
    async def reset(self, ctx):
        """increases the EQ."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player:
            if player.current is None:
                await ctx.send(':asterisk: | Bot is not playing any music.')
            player.reset_equalizer()
            await ctx.send('EQ has been reset')


def setup(bot):
    """
    Setup Music Cog
    """
    bot.add_cog(Music(bot))
