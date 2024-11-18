from discord.ext import commands, tasks
import discord
from dataclasses import dataclass
import datetime
from dotenv import load_dotenv
import os
from playsound import playsound
import yt_dlp as yt
import random
from collections import deque
from discord import FFmpegPCMAudio
import asyncio


load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 1276779190439645197
MAX_SESSION_TIME_MINUTES = 30
NAME = "thog"
tuco_getout = "https://media.discordapp.net/attachments/955285900466724895/1266506597824335882/v0f044gc0000choio6rc77u9ihvg2mm0.mov?ex=66cc49ef&is=66caf86f&hm=a9e2ef50cf8c8010edad5425584ab6d1a6e84d69be9fce0e999f52c962170eab&"
tuco_getout_mp3 = "/Users/stevenmai/Downloads/tuco_getout.mp3"


# Initialize a queue for managing songs
song_queue = deque()


@dataclass
class Session:
    is_active: bool = False
    start_time: int = 0

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
session = Session()

def get_command_list():
    commands_list = [
        "**!hello** - Bot greets you.",
        "**!add** [num1 num2 ...] - Adds numbers.",
        "**!subtract** [num1 num2 ...] - Subtracts numbers.",
        "**!multiply** [num1 num2 ...] - Multiplies numbers.",
        "**!divide** [num1 num2 ...] - Divides numbers.",
        "**!start** - Starts a timed study session.",
        "**!end** - Ends a timed study session and sends the Tuco GET OUT video.",
        "**!tuco** - Plays the Tuco GET OUT sound.",
        "**!GETOUT** - Sends the Tuco GET OUT video.",
        "**!vc** - Joins the voice channel of the user.",
        "**!dip** - Leaves the current voice channel.",
        "**!play** [url/search] - Plays a song by URL or searches YouTube.",
        "**!queue** - Displays the current song queue.",
        "**!skip** - Skips the current song.",
        "**!pause** - Pauses the current song.",
        "**!resume** - Resumes paused playback.",
        "**!stop** - Stops playback and clears the queue.",
        "**!guess** [1-5] - Guess a number between 1 and 5. Guess wrong and you die.",
        "**!commandslist** - Lists all available commands."
    ]
    return "\n".join(commands_list)




@bot.event
async def on_ready():
    print(f"hi it me {NAME} xd")
    
    """
    channels = [ 
        #"animanga", 
        "sizz-bot"]

    for name in channels:
        channel = discord.utils.get(bot.get_all_channels(), name=name)
        if channel:
            await channel.send(f"**It me {NAME} xd**\n\nType **!commandslist** for list of commands")
        else:
            print(f"Channel not found: {name}")
    """


@tasks.loop(minutes=MAX_SESSION_TIME_MINUTES, count=2) #the task should ignore the first instance so it doesnt stop immediately
async def break_reminder():

    if break_reminder.current_loop == 0:
        return 

    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(f"**Take a break pal!** You've been studying for {MAX_SESSION_TIME_MINUTES} minutes already")


@bot.command(
    name='commandslist',
    description='Generates a list of available commands for user interactivity',
    pass_context=True,
)
async def commandslist(ctx):
    command_list = get_command_list()
    await ctx.send(f"**Available Commands:** \n\n{command_list}")


@bot.command(
    name='hello',
    description='Greets the user that typed the command by pinging/mentioning them',
    pass_context=True,
)
async def hello(ctx):
    await ctx.send(f"Hi {ctx.message.author.mention}")


@bot.command(
    name='add',
    description='Performs addition, accepts arrays',
    pass_context=True,
)
async def add(ctx, *arr):

    if not arr:
        await ctx.send("Send numbers to add")
        return

    result = int(arr[0])
    for i in arr[1:]:
        result += int(i)
    await ctx.send(f"Result: {result}")


@bot.command(
    name='subtract',
    description='Performs subtraction, accepts arrays',
    pass_context=True,
)
async def subtract(ctx, *arr):

    if not arr:
        await ctx.send("Send numbers to subtract")
        return

    result = int(arr[0])
    for i in arr[1:]:
        result -= int(i)
    await ctx.send(f"Result: {result}")


@bot.command(
    name='multiply',
    description='Performs multiplication, accepts arrays',
    pass_context=True,
)
async def multiply(ctx, *arr):

    if not arr:
        await ctx.send("Send numbers to multiply")
        return

    result = int(arr[0])
    for i in arr[1:]:
        result *= int(i)
    await ctx.send(f"Result: {result}")


@bot.command(
    name='divide',
    description='Performs division, accepts arrays',
    pass_context=True,
)
async def divide(ctx, *arr):

    if not arr:
        await ctx.send("Send numbers to divide")
        return

    result = float(arr[0])
    for i in arr[1:]:
        num = float(i)
        if num == 0:
            await ctx.send("Can't divide by zero bud")
            return
        result /= num
    await ctx.send(f"Result: {result}")



@bot.command(
    name='start',
    description='Starts a timed study session',
    pass_context=True,
)
async def start(ctx):
    if session.is_active:
        await ctx.send("A session is already active")
        return

    session.is_active = True
    session.start_time = ctx.message.created_at.timestamp()
    human_readable_time = ctx.message.created_at.strftime("%H:%M:%S")
    break_reminder.start()
    await ctx.send(f"New session started at {human_readable_time}")

@bot.command(
    name='end',
    description='Ends a currently active study session; sends the tuco get out video after',
    pass_context=True,
)
async def end(ctx):
    if not session.is_active:
        await ctx.send("There is no active session")
        return
    
    session.is_active = False
    end_time = ctx.message.created_at.timestamp()
    duration = end_time - session.start_time
    human_readable_duration = str(datetime.timedelta(seconds=duration))
    break_reminder.stop()
    await ctx.send(f"Session ended after {human_readable_duration}")
    await ctx.send(tuco_getout)
    playsound(tuco_getout_mp3)


@bot.command(
    name='tuco',
    description='GET OUT',
    pass_context=True,
)
async def tuco(ctx, arg=None):
    """
    if arg == "1":
        await ctx.send(tuco_getout)
    """

    if arg == None:
        playsound(tuco_getout_mp3)



@bot.command(
    name='GETOUT',
    description='GET OUT',
    pass_context=True,
)
async def get_out(ctx, arg=None):
    if arg == None:
        await ctx.send(tuco_getout)
    


@bot.command(
    name='vc',
    description='Joins the current voice channel of the user who typed the command; offers snarky remarks if the user isnt in a voice channel',
    pass_context=True,
)
async def vc(ctx):

    global voice_state
    voice_state = ctx.message.author.voice
    if voice_state is None or voice_state.channel is None:
        await ctx.send("Join a voice channel first bum")
        return

    channel = voice_state.channel
    await channel.connect()
    await ctx.send("Successfully joined the voice channel")
    return True

@bot.command(
    name='dip',
    description='Makes the bot leave its current voice channel; offers yet another snarky remark',
    pass_context=True,
    )
async def dip(ctx):
    server = ctx.message.guild.voice_client
    await server.disconnect()
    await ctx.send(f"Ight fuck you too then, {ctx.message.author.mention}")

"""
@bot.command(
    name='play',
    description='Lets the user play a url of their choice',
    pass_context=True,
)
async def play(ctx, url=None):
    if ctx.voice_client is None:
        await ctx.send(f"{ctx.message.author.mention} isnt in a voice channel")
        return

    if url is None:
        await ctx.send("Please include a url")

    author = ctx.message.author
    voice_channel = author.voice_channel
    vc = await bot.join_voice_channel(voice_channel)

    player = await vc.create_ytdl_player(url)
    player.start()

    await ctx.send(f"Now playing: {url}")
"""


@bot.command(
    name="guess",
    description="Randomly kicks a member from the server; good riddance",
    pass_context=True
)

async def guess(ctx, guess:int):
    if guess < 1 or 5 < guess:
        await ctx.send("It's gotta be between 1 and 5 pal")
        return
    random_number = random.randint(1,5)

    if guess == random_number:
        await bot.kick(reason="Unlucky")
        await ctx.send("Lol")
    else:
        await ctx.send("How about one more try? If you dare")


# Function to play the next song in the queue
async def play_next(ctx):
    if song_queue:
        url = song_queue.popleft()
        try:
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            if not voice_client or not voice_client.is_connected():
                await ctx.send("Bot is not in a voice channel!")
                return

            # Download audio with yt_dlp
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                'quiet': True,
                'outtmpl': 'song.mp3'
            }
            with yt.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Play the downloaded song
            source = FFmpegPCMAudio('song.mp3')
            voice_client.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

            await ctx.send(f"Now playing: {url}")
        except Exception as e:
            await ctx.send(f"Error playing song: {str(e)}")
    else:
        await ctx.send("Queue is empty!")

@bot.command(
    name='play',
    description='Plays a song by URL or searches YouTube if no URL provided.',
    pass_context=True
)
async def play(ctx, *, search=None):
    voice_state = ctx.message.author.voice
    if voice_state is None or voice_state.channel is None:
        await ctx.send("Join a voice channel first!")
        return

    channel = voice_state.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        await channel.connect()

    if search:
        if "http" not in search:
            # Perform YouTube search
            ydl_opts = {"quiet": True}
            with yt.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if info and "entries" in info:
                    video = info["entries"][0]
                    song_queue.append(video["webpage_url"])
                    await ctx.send(f"Added to queue: {video['title']}")
                else:
                    await ctx.send("No results found!")
                    return
        else:
            song_queue.append(search)
            await ctx.send(f"Added to queue: {search}")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command(
    name='queue',
    description='Displays the current song queue.',
    pass_context=True
)
async def queue(ctx):
    if song_queue:
        queue_list = "\n".join([f"{i+1}. {url}" for i, url in enumerate(song_queue)])
        await ctx.send(f"Current Queue:\n{queue_list}")
    else:
        await ctx.send("Queue is empty!")

@bot.command(
    name='skip',
    description='Skips the current song.',
    pass_context=True
)
async def skip(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await play_next(ctx)
    else:
        await ctx.send("No song is currently playing!")

@bot.command(
    name='pause',
    description='Pauses the current song.',
    pass_context=True
)
async def pause(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Playback paused!")
    else:
        await ctx.send("No song is currently playing!")

@bot.command(
    name='resume',
    description='Resumes paused playback.',
    pass_context=True
)
async def resume(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Playback resumed!")
    else:
        await ctx.send("No song is currently paused!")

@bot.command(
    name='stop',
    description='Stops playback and clears the queue.',
    pass_context=True
)
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()

    song_queue.clear()
    await ctx.send("Playback stopped and queue cleared!")





bot.run(DISCORD_BOT_TOKEN)