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

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play',)

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
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    async def track_hook(self, event):
        """
        Track lavalink events
        """
        if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

        if isinstance(event, lavalink.events.TrackStartEvent):
            player = event.player
            notify_channel = player.fetch("channel")
            notify_channel = self.bot.get_channel(notify_channel)
            requester = player.fetch("requestee")
            info = [
                ['Song: ', f'[{player.current.title}]({player.current.uri})'],
                ['Duration: ', f'{parse_duration(player.current.duration/1000)}'],
                ['By: ', f'{player.current.author}'],
                ['Requested By: ', f'{requester}']
            ]
            embed=helpers.embed(title='Now Playing: ', description=f'```css\n{player.current.title}\n```', fields=info)
            await notify_channel.send(embed=embed)

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
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


        if not ctx.author.voice or (ctx.author.voice.channel.id != int(player.channel_id)):
            # Abuse prevention
            return await ctx.send('You\'re not in my voicechannel!')

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await self.connect_to(ctx.guild.id, None)
        await ctx.send('*⃣ | Disconnected.')

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
                await ctx.send('*⃣ | Bot is not playing any music.')

            elif player.paused:
                await ctx.send(':asterisk: | Bot has been unpaused')
                await player.pause(False)
            elif not player.paused:
                await ctx.send(':asterisk: | Bot has been paused')
                await player.pause()

    @commands.command(
        name="current",
        description="Shows the current playing song.",
        usage="current",
        aliases=['np','nowplaying']
    )
    async def current(self,ctx):
        """
        Shows whats poppin
        """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        requester = player.fetch("requestee")
        info = [
                ['Song: ', f'[{player.current.title}]({player.current.uri})'],
                ['Duration: ', f'{parse_duration(player.current.duration/1000)}'],
                ['By: ', f'{player.current.author}']
                ['Requested By: ', f'{requester}']
            ]
        embed=helpers.embed(
            title='Now Playing: ',
            description=f'```css\n{player.current.title}\n```',
            fields=info
        )
        await ctx.send(embed=embed)

    @commands.command(name='queue')
    async def queue(self, ctx, page: int = 1):
        """Shows the queue"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page
        if player.is_playing:
            queue_list = f'`1.` [**{player.current.title}**]({player.current.uri}) | {parse_duration(player.current.duration/1000)}\n'
            playeradd = 1
        else:
            queue_list = ''
            playeradd = 0

        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1 + playeradd}.` [**{track.title}**]({track.uri}) | {parse_duration(track.duration/1000)}\n'

        embed = discord.Embed(colour=discord.Color.blurple(),
                            description=f'**{len(player.queue) + playeradd} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

def setup(bot):
    """
    Setup Music Cog
    """
    bot.add_cog(Music(bot))
