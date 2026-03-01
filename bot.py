import discord
from discord.ext import commands
from discord import app_commands
import wavelink
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
LAVALINK_HOST = os.getenv("LAVALINK_HOST", "lavalink")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", 2333))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await wavelink.NodePool.create_node(
        bot=bot,
        host=LAVALINK_HOST,
        port=LAVALINK_PORT,
        password=LAVALINK_PASSWORD,
        https=False
    )
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def search_track(query: str):
    # Primary: YouTube
    track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
    if track:
        return track

    # Fallback 1: YouTube Music
    track = await wavelink.YouTubeMusicTrack.search(query=query, return_first=True)
    if track:
        return track

    # Fallback 2: SoundCloud
    track = await wavelink.SoundCloudTrack.search(query=query, return_first=True)
    return track

@bot.tree.command(name="play", description="Play a song")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    if not interaction.user.voice:
        return await interaction.followup.send("Join a voice channel first.")

    if not interaction.guild.voice_client:
        player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
    else:
        player = interaction.guild.voice_client

    track = await search_track(query)
    if not track:
        return await interaction.followup.send("No results found.")

    await player.play(track)

    embed = discord.Embed(
        title="🎵 Now Playing",
        description=track.title,
        color=discord.Color.blurple()
    )

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="skip", description="Skip current song")
async def skip(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if player and player.is_playing():
        await player.stop()
        await interaction.response.send_message("⏭ Skipped")
    else:
        await interaction.response.send_message("Nothing playing.")

@bot.tree.command(name="disconnect", description="Disconnect bot")
async def disconnect(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if player:
        await player.disconnect()
        await interaction.response.send_message("Disconnected.")
    else:
        await interaction.response.send_message("Not connected.")

bot.run(TOKEN)
