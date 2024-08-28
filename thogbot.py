from discord.ext import commands, tasks
import discord
from dataclasses import dataclass
import datetime
from dotenv import load_dotenv
import os
from playsound import playsound
import yt_dlp as yt
import random

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 1276779190439645197
MAX_SESSION_TIME_MINUTES = 30
NAME = "thog"
tuco_getout = "https://media.discordapp.net/attachments/955285900466724895/1266506597824335882/v0f044gc0000choio6rc77u9ihvg2mm0.mov?ex=66cc49ef&is=66caf86f&hm=a9e2ef50cf8c8010edad5425584ab6d1a6e84d69be9fce0e999f52c962170eab&"
tuco_getout_mp3 = "/Users/stevenmai/Downloads/tuco_getout.mp3"


#print(f"DISCORD_BOT_TOKEN: {BOT_TOKEN}")

@dataclass
class Session:
    is_active: bool = False
    start_time: int = 0

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
session = Session()

def get_command_list():
    commands_list = [
        "**!hello** - Bot greets you",
        "**!add** [num1 num2 ...] - Add numbers",
        "**!subtract** [num1 num2 ...] - Subtract numbers",
        "**!multiply** [num1 num2 ...] - Multiply numbers",
        "**!divide** [num1 num2 ...] - Divide numbers",
        "**!start** - Start a session",
        "**!end** - End a session",
        "**!tuco** - GET OUT",
        "**!vc** - Joins the voice channel of whoever initiated the command",
        "**!dip** - Leaves the current voice channel", 
        "**!play** - Plays whatever url is provided"

    ]
    return "\n".join(commands_list)



@bot.event
async def on_ready():
    print(f"It me {NAME} xd")
    
    channels = [ 
        #"animanga", 
        "sizz-bot"]

    for name in channels:
        channel = discord.utils.get(bot.get_all_channels(), name=name)
        if channel:
            await channel.send(f"**It me {NAME} xd**\n\nType **!commandslist** for list of commands")
        else:
            print(f"Channel not found: {name}")


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
    name='Divide',
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
async def tuco(ctx):
    playsound(tuco_getout_mp3)
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
    name="randomkick",
    description="Randomly kicks a member from the server; good riddance",
    pass_context=True
)

async def randomkick(ctx, guess):
    await ctx.send("Guess a number 1-10")
    random_number = int(input(random.randint(1,10)))
    guess = int(input())

    if guess == random_number:
        await bot.kick(reason="Unlucky")
        await ctx.send("Lol")



bot.run(DISCORD_BOT_TOKEN)