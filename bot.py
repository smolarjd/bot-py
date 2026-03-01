import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import yt_dlp
from database import add_song, clear_queue
from player import MusicPlayer

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

player = MusicPlayer(bot)


class ControlView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.guild = guild

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("Skipped.")
        else:
            await interaction.response.send_message("Nothing playing.")

    @discord.ui.button(label="⏹ Stop", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button):
        clear_queue(interaction.guild.id)
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("Stopped & cleared queue.")

    @discord.ui.button(label="🔁 Autoplay", style=discord.ButtonStyle.success)
    async def autoplay(self, interaction: discord.Interaction, button):
        player.autoplay = not player.autoplay
        await interaction.response.send_message(f"Autoplay: {player.autoplay}")


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot ready")


@bot.event
async def on_voice_state_update(member, before, after):
    await player.auto_reconnect(member, before, after)


@bot.tree.command(name="play", description="Play a YouTube song")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    if not interaction.user.voice:
        return await interaction.followup.send("Join a voice channel.")

    vc = interaction.guild.voice_client
    if not vc:
        vc = await interaction.user.voice.channel.connect()

    ytdl = yt_dlp.YoutubeDL({"quiet": True})
    info = ytdl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
    url = info["webpage_url"]

    add_song(interaction.guild.id, url)

    if not vc.is_playing():
        await player.play_next(interaction.guild, interaction.channel)

    embed = discord.Embed(
        title="Added to Queue",
        description=info["title"],
        color=discord.Color.green()
    )

    await interaction.followup.send(embed=embed, view=ControlView(interaction.guild))


bot.run(TOKEN)
