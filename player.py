import discord
import yt_dlp
import asyncio
import os
from database import get_queue, remove_first

ytdl = yt_dlp.YoutubeDL({
    "format": "bestaudio",
    "quiet": True
})

ffmpeg_options = {
    "options": "-vn"
}


class MusicPlayer:

    def __init__(self, bot):
        self.bot = bot
        self.autoplay = True

    async def play_next(self, guild, channel):
        queue = get_queue(guild.id)
        if not queue:
            return

        url = queue[0]
        remove_first(guild.id)

        with ytdl.extract_info(url, download=False) as info:
            stream = info["url"]
            title = info.get("title")

        vc = guild.voice_client
        if not vc:
            return

        vc.play(
            discord.FFmpegPCMAudio(stream, **ffmpeg_options),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(guild, channel), self.bot.loop)
        )

        embed = discord.Embed(
            title="🎵 Now Playing",
            description=title,
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed)

    async def auto_reconnect(self, member, before, after):
        if not os.getenv("AUTO_RECONNECT", "true") == "true":
            return

        if member.id != self.bot.user.id:
            return

        if before.channel and not after.channel:
            await asyncio.sleep(3)
            try:
                await before.channel.connect()
            except:
                pass
