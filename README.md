# 🎵 Tune — High Quality Discord Music Bot

**Tune** is a high-performance Discord music bot built in Python using `discord.py` and `yt-dlp`.  
It streams music directly from YouTube in **high quality**, supports **slash commands**, **queues**, and **auto voice management**.

---

## ✨ Features

✅ Slash commands (`/play`, `/pause`, `/resume`, `/skip`, `/stop`, `/queue`)  
✅ High-quality audio (192kbps+) via FFmpeg  
✅ YouTube search and direct URL playback  
✅ Auto-disconnect when queue is empty  
✅ Works with YouTube playlists or single tracks  
✅ Lightweight, simple Python codebase  

---

## ⚙️ Requirements

- Python **3.11+** (tested with 3.14)
- FFmpeg installed and added to your PATH
- A valid **Discord Bot Token**

---

## 🧰 Installation (Local Setup)

### 1️⃣ Clone or Download

```git-bash
git clone https://github.com/devXNaresh/tune-discord-bot.git
cd tune-discord-bot
```
2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
3️⃣ Install FFmpeg
🪟 Windows:
Download from https://www.gyan.dev/ffmpeg/builds/
Extract to:

```makefile
C:\ffmpeg\bin
```
Then add that folder to your PATH environment variable.

🐧 Linux (Debian/Ubuntu):
```bash
sudo apt update && sudo apt install ffmpeg -y
```

4️⃣ Add Your Token
Open bot.py and replace:

```python
YOUR_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
```
Get your token from the Discord Developer Portal.

▶️ Running the Bot
```bash
python bot.py
```
You should see:

```
✅ Logged in as Tune#1234
✅ Slash commands synced globally.
```
Then invite your bot to your server using the OAuth2 URL from the Discord Developer Portal.

## 💬 Commands

| Command | Description |
|----------|-------------|
| `/play <song or URL>` | Play a song or queue one |
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/skip` | Skip current track |
| `/stop` | Stop playback and leave VC |
| `/queue` | Show current queue |


---

## 🧠 Credits

**Developer & Maintainer:** [Naresh](https://github.com/devXNaresh)

- 🧩 Originally developed as **Tune**, an open-source Discord music bot template.
- 💻 Built with Python, `discord.py`, `yt-dlp`, and `FFmpeg`.
- 💬 For help or collaboration, reach out on Discord: **nareshgameryt**

---
