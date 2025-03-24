import discord
from discord.ext import commands
import wavelink
import os
from typing import Optional
import asyncio

class MusicPlayer(commands.Cog):
    """A cog for handling music playback in voice channels."""
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.connect_nodes())
        self._node_retries = 0
        self._max_retries = 5

    async def connect_nodes(self):
        """Connect to Lavalink nodes with retry mechanism."""
        await self.bot.wait_until_ready()
        while self._node_retries < self._max_retries:
            try:
                node = wavelink.Node(
                    uri=f'http://{os.getenv("LAVALINK_HOST")}:{os.getenv("LAVALINK_PORT")}',
                    password=os.getenv("LAVALINK_PASSWORD")
                )
                await wavelink.Pool.connect(nodes=[node], client=self.bot)
                print("Connected to Lavalink node!")
                return
            except Exception as e:
                self._node_retries += 1
                print(f"Failed to connect to Lavalink node (attempt {self._node_retries}/{self._max_retries}): {e}")
                if self._node_retries < self._max_retries:
                    await asyncio.sleep(5)  # Wait 5 seconds before retrying
                else:
                    print("Max retries reached. Please check your Lavalink server.")

    async def cog_unload(self):
        """Cleanup when the cog is unloaded."""
        for node in wavelink.Pool.nodes:
            await node.disconnect()

    def get_player(self, ctx) -> Optional[wavelink.Player]:
        """Get the voice client player for the current context."""
        if not ctx.voice_client:
            return None
        return ctx.voice_client

    @commands.command()
    async def join(self, ctx):
        """Join the user's voice channel."""
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel first!")
        
        channel = ctx.author.voice.channel
        try:
            player = await channel.connect(cls=wavelink.Player)
            await ctx.send(f"Joined #{channel.name}!")
        except Exception as e:
            await ctx.send(f"Failed to join voice channel: {e}")

    @commands.command()
    async def play(self, ctx, *, search: str):
        """Play a song from YouTube."""
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        
        player = self.get_player(ctx)
        if not player:
            return await ctx.send("Failed to get player. Please try again.")

        try:
            # Check if the input is a URL
            if search.startswith(('http://', 'https://')):
                try:
                    track = await wavelink.Playable.from_url(search)
                    await player.play(track)
                    await ctx.send(f"Now playing: {track.title} - {track.author}")
                    return
                except Exception as e:
                    print(f"Error loading URL: {e}")
                    return await ctx.send("Failed to load the URL. Please try again.")

            # If not a URL, search for the track
            print(f"Attempting to search for: {search}")
            tracks = await wavelink.Playable.search(search, source=wavelink.TrackSource.YouTube)
            
            if not tracks:
                return await ctx.send("No songs found! Try being more specific with your search.")
            
            # Send search results
            search_results = "**Search Results:**\n"
            for i, track in enumerate(tracks[:5], 1):
                duration = str(track.duration).split('.')[0]  # Remove milliseconds
                search_results += f"{i}. {track.title} - {track.author} ({duration})\n"
            
            search_results += "\nPlease select a track by typing a number (1-5) or 'cancel' to cancel."
            search_msg = await ctx.send(search_results)
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                response = await self.bot.wait_for('message', timeout=15.0, check=check)
                await search_msg.delete()
                await response.delete()
                
                if response.content.lower() == 'cancel':
                    return await ctx.send("Search cancelled.")
                
                try:
                    selection = int(response.content)
                    if selection < 1 or selection > min(5, len(tracks)):
                        return await ctx.send("Invalid selection. Please choose a number between 1 and 5.")
                    
                    track = tracks[selection - 1]
                    await player.play(track)
                    await ctx.send(f"Now playing: {track.title} - {track.author}")
                except ValueError:
                    return await ctx.send("Invalid input. Please enter a number or 'cancel'.")
                    
            except TimeoutError:
                await search_msg.delete()
                return await ctx.send("Search timed out. Please try again.")
                
        except Exception as e:
            print(f"Error in play command: {e}")
            await ctx.send("An error occurred while searching. Please try again in a few moments.")

    @commands.command()
    async def stop(self, ctx):
        """Stop the current song."""
        player = self.get_player(ctx)
        if not player:
            return await ctx.send("I'm not playing anything!")
        
        await player.stop()
        await ctx.send("Stopped playing")

    @commands.command()
    async def leave(self, ctx):
        """Leave the voice channel."""
        player = self.get_player(ctx)
        if not player:
            return await ctx.send("I'm not in a voice channel!")
        
        await player.disconnect()
        await ctx.send("Left the voice channel")

    @commands.command()
    async def pause(self, ctx):
        """Pause the current song."""
        player = self.get_player(ctx)
        if not player:
            return await ctx.send("I'm not playing anything!")
        
        await player.pause()
        await ctx.send("Paused ⏸")

    @commands.command()
    async def resume(self, ctx):
        """Resume the current song."""
        player = self.get_player(ctx)
        if not player:
            return await ctx.send("I'm not playing anything!")
        
        await player.resume()
        await ctx.send("Resumed ▶")

    @commands.command()
    async def skip(self, ctx):
        """Skip the current song."""
        player = self.get_player(ctx)
        if not player:
            return await ctx.send("I'm not playing anything!")
        
        if not player.queue:
            return await ctx.send("No songs in queue to skip to!")
        
        await player.stop()
        await ctx.send("Skipped current song")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Set the volume (0-100)."""
        player = self.get_player(ctx)
        if not player:
            return await ctx.send("I'm not playing anything!")
        
        if not 0 <= volume <= 100:
            return await ctx.send("Volume must be between 0 and 100!")
        
        await player.set_volume(volume)
        await ctx.send(f"Volume set to {volume}%")

    @commands.command()
    async def queue(self, ctx):
        """Show the current queue."""
        player = self.get_player(ctx)
        if not player:
            return await ctx.send("I'm not playing anything!")
        
        if not player.queue:
            return await ctx.send("The queue is empty!")
        
        queue_list = []
        for i, track in enumerate(player.queue, 1):
            duration = str(track.duration).split('.')[0]
            queue_list.append(f"{i}. {track.title} - {track.author} ({duration})")
        
        await ctx.send(f"**Current Queue:**\n" + "\n".join(queue_list))

    @commands.command()
    async def nowplaying(self, ctx):
        """Show information about the currently playing song."""
        player = self.get_player(ctx)
        if not player or not player.current:
            return await ctx.send("Nothing is currently playing!")
        
        track = player.current
        duration = str(track.duration).split('.')[0]
        await ctx.send(f"**Now Playing:**\n{track.title} - {track.author}\nDuration: {duration}")

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
