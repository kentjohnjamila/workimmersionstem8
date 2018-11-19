import asyncio
import discord
from discord.ext import commands
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')
import youtube_dl

def __init__(self, bot):
        self.bot = bot

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = ':musical_note: `{0.title}`'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' - `Length: {0[0]}m {0[1]}s`'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()
class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Joins a voice channel."""
        embed = discord.Embed(color = discord.Color(0).gold())        
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            embed.description = ":x: This is not a voice channel, nice try"
            await self.bot.say(embed=embed)
        except discord.InvalidArgument:
            embed.description = ":x: This is not a voice channel, nice try"
            await self.bot.say('`This is not a voice channel...`')
        else:
            embed.description = ":speaker: Ready to play audio in {}".format(channel.name)
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        embed = discord.Embed(color = discord.Color(0).gold())
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            embed.description = ':x: Are you sure youre in a channel?'
            await self.bot.say(embed=embed)
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            embed.description = ":beginner: Musika has been summoned"           
            await state.voice.move_to(summoned_channel)
            await self.bot.say(embed=embed)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def disconnect(self, ctx):
        """Stops playing audio and disconnect the voice channel."""
        embed = discord.Embed(color = discord.Color(0).gold())        
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
            embed.description = ":wave: Disconnect from voice channel"
            await self.bot.say(embed=embed)
        except:
            pass
             
    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing."""
        embed = discord.Embed(color = discord.Color(0).gold())        
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            embed.description = ":mag_right: searching, please wait..."
            await self.bot.say(embed=embed)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 1
            entry = VoiceEntry(ctx.message, player)            
            embed.description = ":arrow_double_up: Queued" + str(entry)
            await self.bot.send_message(ctx.message.channel, embed=embed)
            await state.songs.put(entry)
            await self.bot.send_message(ctx.message.channel)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""
        embed = discord.Embed(color = discord.Color(0).gold()) 
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            embed.description = ":level_slider: Volume is now {:.0%}".format(player.volume)
            await self.bot.say(embed=embed)
            
    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        embed = discord.Embed(color = discord.Color(0).gold())         
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()
            embed.description = ":musical_note: Resumed"
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        embed = discord.Embed(color = discord.Color(0).gold())        
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()
            embed.description = ':pause_button: Music Paused'
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        embed = discord.Embed(color = discord.Color(0).gold())         
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
            embed.description = ":stop_button: Music stopped and disconnected from the voice channel"
            await self.bot.say(embed=embed)
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """To skip a song."""
        embed = discord.Embed(color = discord.Color(0).gold())
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            embed.description = ':thumbsdown: Not playing any music right now - Use `?play`'
            await self.bot.say(embed=embed)
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            embed.description =":track_next: Song Skipped"
            await self.bot.say(embed=embed)
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 1:
                embed.description =":track_next: Song Skipped"                
                await self.bot.say(embed=embed)
                state.skip()
            else:
                await self.bot.say('Skip vote added, currently at [{}/1]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)
    async def songinfo(self, ctx):
        """Shows the info of the currently playing song."""
        embed = discord.Embed(color = discord.Color(0).gold())
        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            embed.description = ':thumbsdown: Not playing any music right now - Use `?play`'
            await self.bot.say(embed=embed)
        else:
            embed.description = 'Now playing {}'.format(state.current)
            await self.bot.say(embed=embed)         


def setup(bot):
    bot.add_cog(Music(bot))
    print("___________________________")
    print("Music System Ready")