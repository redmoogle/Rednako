# pylint: disable=E1101
# error ignore for non-standard module

"""

Rednako: Code is from https://raw.githubusercontent.com/Devoxin/Lavalink.py/master/examples/music.py

This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.

Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""
import re

import discord
import lavalink
from discord.ext import commands
import config
import math
import helpers
config = config.Config('./config.cfg')

def DJConfig(ctx):
    if(config['enable_dj_role']):
        for role in ctx.author.roles:
            if(config['dj_role'] == role.name):
                return True
            elif(config['dj_role'] == str(role.id)):
                return True
        return False
    return True

def parse_duration(duration: int):
    seconds = divmod(duration, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
        duration.append('{} days'.format(days))
    if hours > 0:
        duration.append('{} hours'.format(hours))
    if minutes > 0:
        duration.append('{} minutes'.format(minutes))
    if seconds > 0:
        duration.append('{} seconds'.format(seconds))
    return duration

url_rx = re.compile(r'https?://(?:www\.)?.+')


class Music(commands.Cog):
    """
    Play your weeb songs
    """
    def __init__(self, bot):
        self.bot = bot
        self.init_lavalink()

    async def init_lavalink(self):
        await lavalink.initialize(
            self.bot, host='localhost', password='youshallnotpass',
            rest_port=2332, ws_port=2333
        )

    async def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        await lavalink.close()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
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
        
        player = await lavalink.connect(ctx.author.voice.channel)

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

    @commands.command(
        name="play",
        description="play music.",
        usage="play [song]",
        aliases=['p']
        )
    async def search_and_play(self, ctx, search_terms):
        if(not ctx.voice_state.voice) and (ctx.author.voice):
            destination = ctx.author.voice.channel
        else:
            return await ctx.send('You\'re not in a voice channel')
        player = await lavalink.connect(destination)
        tracks = await player.search_yt(search_terms)
        track = tracks[0]
        player.add(track)

        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = 'Track Enqueued'
        embed.description = f'[{track.title}]({track.uri})'

        if player.is_playing:
            await ctx.send(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()
            info = [
                ['Song: ', f'{player.current.title}(f"https://youtube.com/watch?v={player.current.identifier})'],
                ['Duration: ', f'{parse_duration(player.current.length)}'],
                ['Requested by: ', f'{player.current.requester}']
            ]
            embed=helpers.embed(title='Now Playing: ', description=f'```css\n{player.current.title}\n```', thumbnail=player.current.thumbnail, fields=info)
            await ctx.send(embed=embed)

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            # We can't disconnect, if we're not connected.
            return await ctx.send('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
            # may not disconnect the bot.
            return await ctx.send('You\'re not in my voicechannel!')

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await self.connect_to(ctx.guild.id, None)
        await ctx.send('*⃣ | Disconnected.')

    @commands.check(DJConfig)
    @commands.command(
        name='pause',
        brief='pauses the song'
    )
    async def pause(self, ctx):
        """pauses the player."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if(player):
           await player.stop()
        if not player.is_playing:
            await ctx.send('*⃣ | Bot is not playing any music.')

    @commands.command(
        name="current",
        description="Shows the current playing song.",
        usage="current",
        aliases=['np','nowplaying']
        )
    async def current(self,ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed=discord.Embed(title=player.current.title,url=f"https://youtube.com/watch?v={player.current.identifier}")
        await ctx.send(embed=embed)

    @commands.command(name='queue')
    async def queue(self, ctx, page: int = 1):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page
        if player.is_playing:
            queue_list = f'[**{player.current.title}**](https://youtube.com/watch?v={player.current.identifier})\n'
            playeradd = 1
        else:
            queue_list = ''
            playeradd = 0

        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [**{track.title}**]({track.uri})\n'

        embed = discord.Embed(colour=discord.Color.blurple(),
                            description=f'**{len(player.queue) + playeradd} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.check(DJConfig)
    @commands.command(
        name = "clear",
        description="Clears all of the currently playing songs and makes the bot disconnect."
    )
    async def clear_queue(self,ctx):
        try:
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)
            if ctx.author.voice is not None and ctx.author.voice.channel.id == int(player.channel_id):
                if player.is_playing:
                    while player.is_playing:
                        await player.skip()
                    await ctx.channel.send("Songs Cleared.")
                else:
                    await ctx.channel.send("Nothing playing to clear.")
            else: 
                await ctx.channel.send("Please join the same voice channel as me.")
        except:
            await ctx.channel.send("Nothing playing.")


def setup(bot):
    bot.add_cog(Music(bot))
