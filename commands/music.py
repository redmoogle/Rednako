# -*- coding: utf-8 -*-
# pylint: disable=E1101
# error ignore for non-standard module

"""
Copyright (c) 2019 Valentin B.

A simple music bot written in discord.py using youtube-dl.

Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.

Requirements:

Python 3.5+
pip install -U discord.py pynacl youtube-dl

You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.

Rednako: Go checkout his work here! https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
"""

import asyncio
import functools
import itertools
import math
import random
import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
from youtubesearchpython import SearchVideos
from django.core.validators import URLValidator
import config
import helpers
config = config.Config('./config.cfg')

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

def DJConfig(ctx):
    if(config['enable_dj_role']):
        for role in ctx.author.roles:
            if(config['dj_role'] == role.name):
                return True
            elif(config['dj_role'] == str(role.id)):
                return True
        return False
    return True

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(title)s',
        'restrictfilenames': True,
        'noplaylist': False,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()
        validate = URLValidator()
        try:
            validate(search)
        except:
            search = list(SearchVideos(search, offset = 1, mode = "list", max_results = 1).result())[0][3]

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if 'entries' not in data:
            process_info = data

        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            return await ctx.send(f'Could not fetch `{webpage_url}`')

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    return await ctx.send(f'Could not retrieve any matches for `{webpage_url}`')

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
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

        return ', '.join(duration)


class Song(commands.Cog):
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        info = [
            ['Duration: ',      f'{self.source.duration}'],
            ['Requester: ',     f'{self.requester}'],
            ['Uploader: ',      f'[{self.source.uploader}]({self.source.uploader_url})'],
            ['URL: ',           f'[Click]({self.source.url})']
        ]
        embed=helpers.embed(title='Now Playing: ', description=f'```css\n{self.source.title}\n```', thumbnail=self.source.thumbnail, fields=info)
        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    return self.bot.loop.create_task(self.stop())

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    """
    Play Music
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx):
        if ctx.guild:
            return True
        return False

    async def cog_before_invoke(self, ctx):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx, error: commands.CommandError):
        print(f'Error: {error}') # Logging

    @commands.command(
        name='join',
        description='makes the bot join your channel',
        invoke_without_subcommand=True
    )
    async def _join(self, ctx):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            return await ctx.voice_state.voice.move_to(destination)

        ctx.voice_state.voice = await destination.connect()

    @commands.check(DJConfig)
    @commands.command(
        name='summon',
        description='summons bot to your channel'
    )
    async def _summon(self, ctx, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.

        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            return await ctx.send('You are not connected to a voice channel.', delete_after=3)

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            return await ctx.voice_state.voice.move_to(destination)

        ctx.voice_state.voice = await destination.connect()

    @commands.check(DJConfig)
    @commands.command(
        name='leave',
        description='leave channel',
        aliases=['disconnect']
    )
    async def _leave(self, ctx):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.', delete_after=3)

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(
        name='volume',
        description='change volume',
        aliases=['vol', 'v']
    )
    async def _volume(self, ctx, *, volume: int):
        """Sets the volume of the player."""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        if 0 >= volume >= 100:
            return await ctx.send('Volume must be between 0 and 100')

        ctx.voice_state.current.source.volume = volume / 100
        await ctx.send(f'Volume of the player set to {volume}%')

    @commands.command(
        name='playing',
        description='see whats playing',
        aliases=['current', 'now']
    )
    async def _now(self, ctx):
        """Displays the currently playing song."""

        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.check(DJConfig)
    @commands.command(
        name='pause',
        description='pause audio output'
    )
    async def _pause(self, ctx):
        """Pauses the currently playing song."""

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.check(DJConfig)
    @commands.command(
        name='resume',
        description='resume audio output'
    )
    async def _resume(self, ctx):
        """Resumes a currently paused song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.check(DJConfig)
    @commands.command(
        name='stop',
        description='clears queue and current audio'
    )
    async def _stop(self, ctx):
        """Stops playing song and clears the queue."""
        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(
        name='skip',
        description='skip a song'
    )
    async def _skip(self, ctx):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """
        totalmembers = -1 # dont include bot
        for _ in ctx.guild.voice_client.channel.members:
            totalmembers += 1

        totalmembers = round(totalmembers/2)

        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')

        voter = ctx.message.author
        if not ctx.author.voice:
            return await ctx.send('You are not in a voice channel')

        if(ctx.author.voice.channel != ctx.guild.voice_client.channel):
            return await ctx.send('You are not in the same voice channel')

        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()
            return await ctx.send('Song skipped by requester')

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= totalmembers:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send(f'Skip vote added, currently at **{total_votes}/{totalmembers}**')

        else:
            await ctx.send('You have already voted to skip this song.', delete_after=3)

    @commands.command(
        name='queue',
        description='show queue',
        aliases=['q']
    )
    async def _queue(self, ctx, *, page: int = 1):
        """Shows the player's queue.

        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.check(DJConfig)
    @commands.command(
        name='shuffle',
        description='time to get funky'
    )
    async def _shuffle(self, ctx):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.check(DJConfig)
    @commands.command(
        name='remove',
        description='get rid of trash'
    )
    async def _remove(self, ctx, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.check(DJConfig)
    @commands.command(
        name='loop',
        description='loops current song'
    )
    async def _loop(self, ctx):
        """Loops the currently playing song.

        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(
        name='play',
        description='play a song'
    )
    async def _play(self, ctx, *, search: str):
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except Exception as error:
                return await ctx.send(f'An error occurred while processing this request: {error}')
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send(f'Queued up: {source}')

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('You are not connected to any voice channel.', delete_after=3)

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
               return await ctx.send('Bot is already in a voice channel.', delete_after=3)

def setup(bot):
    bot.add_cog(Music(bot))