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
from modules import json
from modules import helpers

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

async def create(bot):
    """
    Create lavalink instance
    """
    await lavalink.initialize(
        bot, host='localhost', password='youshallnotpass',
        rest_port=2333, ws_port=2333
    )

class Music(commands.Cog):
    """
    Play your weeb songs
    """
    def __init__(self, bot):
        self.bot = bot
        loop = asyncio.get_event_loop()
        loop.create_task(create(self.bot))

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

    def djconfig(self):
        """
        Checks config to see if that guild has defined a DJ role
        """
        def checkdj(self, ctx):
            guildrole = json.read_file(self.bot, ctx, 'djmode', None)
            if guildrole is None:
                return True
            print(f'Guildrole is not None: Is {guildrole}')
            return commands.has_role(int(guildrole))
        return commands.check(checkdj)

    async def handle_lavalink_events(self, player: lavalink.Player, event_type: lavalink.LavalinkEvents, extra = None):
        """
        Lavalink events arent sent here
        """
        if extra is None: # Placeholder so pylint doesnt get angry
            pass
        current_channel = player.channel
        if not current_channel:
            return

        if event_type == lavalink.LavalinkEvents.TRACK_START:
            notify_channel = player.fetch("channel")
            notify_channel = self.bot.get_channel(notify_channel)
            info = [
                ['Song: ', f'[{player.current.title}]({player.current.uri})'],
                ['Duration: ', f'{parse_duration(player.current.length/1000)}'],
                ['Requested by: ', f'{player.current.requester}']
            ]
            embed=helpers.embed(title='Now Playing: ', description=f'```css\n{player.current.title}\n```', thumbnail=player.current.thumbnail, fields=info)
            await notify_channel.send(embed=embed)

        if event_type == lavalink.LavalinkEvents.QUEUE_END:
            await player.disconnect()


    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('Join a voicechannel first.')

        player = await lavalink.connect(ctx.author.voice.channel)
        lavalink.register_event_listener(self.handle_lavalink_events)

        permissions = ctx.author.voice.channel.permissions_for(ctx.me)

        if not permissions.connect or not permissions.speak:  # Check user limit too?
            raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')
        if ctx.voice_client:
            if int(player.channel.id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    @commands.command(
        name="play",
        description="play music.",
        usage="play [song]",
        aliases=['p']
    )
    async def search_and_play(self, ctx, *, search_terms):
        """
        Plays a song will search yt if no link is provided
        """
        player = lavalink.get_player(ctx.guild.id)
        if(not ctx.voice_client) and (ctx.author.voice):
            destination = ctx.author.voice.channel
        else:
            if player is None:
                player = await lavalink.connect(destination)
        results = await player.search_yt(search_terms)
        track = results.tracks[0]
        player.add(ctx.author, track)
        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)

        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = 'Track Enqueued'
        embed.description = f'[{track.title}]({track.uri})'

        if player.is_playing:
            await ctx.send(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

    @commands.check(djconfig)
    @commands.command(aliases=['dc', 'stop'])
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = lavalink.get_player(ctx.guild.id)


        if not ctx.author.voice or (ctx.author.voice.channel.id != int(player.channel.id)):
            # Abuse prevention
            return await ctx.send('You\'re not in my voicechannel!')

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await player.disconnect()
        await ctx.send('*⃣ | Disconnected.')

    @commands.check(djconfig)
    @commands.command(
        name='pause',
        brief='pauses the song'
    )
    async def pause(self, ctx):
        """pauses the player."""
        player = lavalink.get_player(ctx.guild.id)
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
        player = lavalink.get_player(ctx.guild.id)
        info = [
                ['Song: ', f'[{player.current.title}]({player.current.uri})'],
                ['Duration: ', f'{parse_duration(player.current.length/1000)}'],
                ['Requested by: ', f'{player.current.requester}']
            ]
        embed=helpers.embed(
            title='Now Playing: ',
            description=f'```css\n{player.current.title}\n```',
            thumbnail=player.current.thumbnail,
            fields=info
        )
        await ctx.send(embed=embed)

    @commands.command(name='queue')
    async def queue(self, ctx, page: int = 1):
        """Shows the queue"""
        player = lavalink.get_player(ctx.guild.id)

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page
        if player.is_playing:
            queue_list = f'`1.` [**{player.current.title}**]({player.current.uri}) | {parse_duration(player.current.length/1000)}\n'
            playeradd = 1
        else:
            queue_list = ''
            playeradd = 0

        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1 + playeradd}.` [**{track.title}**]({track.uri}) | {parse_duration(track.length/1000)}\n'

        embed = discord.Embed(colour=discord.Color.blurple(),
                            description=f'**{len(player.queue) + playeradd} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

def setup(bot):
    """
    Setup Music Cog
    """
    bot.add_cog(Music(bot))
