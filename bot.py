import discord
from discord.ext import commands
import yt_dlp
import asyncio
import logging


# ────────────────────────────────────────────────
# BOT TOKEN
YOUR_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN" # Replace with your actual bot token
# ────────────────────────────────────────────────





# CONFIGURATION


intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

logging.basicConfig(level=logging.INFO)

queues = {}

# High-quality, fast yt_dlp config
ydl_opts = {
    'format': 'bestaudio[abr>=192]/bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'default_search': 'ytsearch',
    'extract_flat': 'in_playlist', 
    'source_address': '0.0.0.0'
}

# Better streaming performance
ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 512k'
}


# QUEUE HANDLING

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = asyncio.Queue()
    return queues[guild_id]


# PLAYBACK LOGIC

async def play_next(interaction, vc):
    queue = get_queue(interaction.guild.id)
    if queue.empty():
        await asyncio.sleep(2)
        await vc.disconnect()
        await interaction.channel.send("✅ Queue empty. Leaving VC.")
        return

    url, title = await queue.get()
    await interaction.channel.send(f"🎶 Now playing: **{title}**")

    # yt-dlp config
    ydl_opts_stream = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'outtmpl': '-',
    }

    ffmpeg_opts_stream = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -loglevel quiet'
    }

    try:
        # Extract direct audio URL using yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts_stream) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            audio_url = info.get('url')
            if not audio_url:
                await interaction.channel.send(f"❌ Could not extract audio for **{title}**.")
                await play_next(interaction, vc)
                return

        # Stream using ffmpeg directly from the extracted URL
        source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts_stream)

        def after_playing(error):
            if error:
                logging.error(f"Playback error: {error}")
            fut = asyncio.run_coroutine_threadsafe(play_next(interaction, vc), bot.loop)
            try:
                fut.result()
            except Exception as e:
                logging.error(f"Error in after_playing: {e}")

        vc.play(source, after=after_playing)

    except Exception as e:
        await interaction.channel.send(f"❌ Error playing **{title}**: {e}")
        logging.error(e)
        await play_next(interaction, vc)





# COMMAND HANDLERS

async def handle_play(interaction, query):
    await interaction.response.defer()

    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    author = interaction.user

    if not vc:
        if author.voice:
            channel = author.voice.channel
            vc = await channel.connect()
            await interaction.followup.send(f"✅ Joined `{channel}`.")
        else:
            await interaction.followup.send("❌ You must be in a voice channel.")
            return

    await interaction.followup.send("🎧 Fetching audio...")

    # Fast metadata fetch
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        url = info.get('webpage_url', query)
        title = info.get('title', query)

    queue = get_queue(interaction.guild.id)
    await queue.put((url, title))

    if not vc.is_playing():
        await play_next(interaction, vc)
    else:
        await interaction.channel.send(f"✅ Added to queue: **{title}**")


# EVENTS

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        await tree.sync()  
        print("✅ Slash commands synced globally.")
    except Exception as e:
        print(f"❌ Sync failed: {e}")


# SLASH COMMANDS

@tree.command(name="play", description="Play or queue a song from YouTube")
async def play_cmd(interaction: discord.Interaction, query: str):
    await handle_play(interaction, query)

@tree.command(name="pause", description="Pause the current song")
async def pause_cmd(interaction: discord.Interaction):
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸ Paused.")
    else:
        await interaction.response.send_message("❌ Nothing to pause.")

@tree.command(name="resume", description="Resume paused song")
async def resume_cmd(interaction: discord.Interaction):
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Resumed.")
    else:
        await interaction.response.send_message("❌ Nothing to resume.")

@tree.command(name="skip", description="Skip current song")
async def skip_cmd(interaction: discord.Interaction):
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭ Skipped.")
    else:
        await interaction.response.send_message("❌ Nothing to skip.")

@tree.command(name="stop", description="Stop music and leave VC")
async def stop_cmd(interaction: discord.Interaction):
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if vc:
        queue = get_queue(interaction.guild.id)
        while not queue.empty():
            queue.get_nowait()
        vc.stop()
        await vc.disconnect()
        await interaction.response.send_message("🛑 Stopped & left VC.")
    else:
        await interaction.response.send_message("❌ Not connected to VC.")

@tree.command(name="queue", description="Show the current music queue")
async def queue_cmd(interaction: discord.Interaction):
    queue = get_queue(interaction.guild.id)
    if queue.empty():
        await interaction.response.send_message("🎶 Queue is empty.")
        return
    msg = "**🎵 Current Queue:**\n"
    for i, item in enumerate(list(queue._queue), start=1):
        msg += f"{i}. {item[1]}\n"
    await interaction.response.send_message(msg)



bot.run(YOUR_BOT_TOKEN)
