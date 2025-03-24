import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import wavelink

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load cogs
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded extension: {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load extension {filename}: {e}")

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')
    await load_extensions()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
