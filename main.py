import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Bot setup with all required intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Connected to Discord Gateway')
    
    # Load the tasks cog
    try:
        await bot.load_extension('cogs.tasks')
        print('Loaded tasks cog')
    except Exception as e:
        print(f'Error loading tasks cog: {e}')
        return

    # Sync commands with Discord
    try:
        # First, try syncing to a specific guild
        if bot.guilds:
            guild = bot.guilds[0]  # Get the first guild the bot is in
            print(f'\nSyncing commands to guild: {guild.name} (ID: {guild.id})')
            synced = await bot.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to guild')
            
            # Debug: List all available commands
            print("\nAvailable Commands:")
            for cmd in bot.tree.get_commands():
                print(f"- /{cmd.name}: {cmd.description}")
        else:
            print("No guilds found! Make sure the bot is in at least one server.")
    except Exception as e:
        print(f'Error syncing commands: {e}')
        print(f'Error type: {type(e)}')
        print(f'Error details: {str(e)}')

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
