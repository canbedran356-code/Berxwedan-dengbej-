import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("music-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

QUEUE = {}

# 🎶 YOUTUBE SES ÇEKME
def get_audio(query):
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        return info["url"]

# ▶️ PLAY
@app.on_message(filters.command("play") & filters.group)
async def play(_, message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        return await message.reply("❗ Şarkı adı yaz")

    query = " ".join(message.command[1:])
    url = get_audio(query)

    await call.join_group_call(
        chat_id,
        AudioPiped(url)
    )

    await message.reply(f"🎶 Çalıyor: {query}")

# ⏸ PAUSE
@app.on_message(filters.command("pause") & filters.group)
async def pause(_, message):
    await call.pause_stream(message.chat.id)
    await message.reply("⏸ Duraklatıldı")

# ▶️ RESUME
@app.on_message(filters.command("resume") & filters.group)
async def resume(_, message):
    await call.resume_stream(message.chat.id)
    await message.reply("▶️ Devam ediyor")

# ⏭ SKIP
@app.on_message(filters.command("skip") & filters.group)
async def skip(_, message):
    await call.leave_group_call(message.chat.id)
    await message.reply("⏭ Geçildi")

# ❌ LEAVE
@app.on_message(filters.command("leave") & filters.group)
async def leave(_, message):
    await call.leave_group_call(message.chat.id)
    await message.reply("👋 Çıktım")

# 🧪 TEST
@app.on_message(filters.command("test"))
async def test(_, message):
    await message.reply("✅ Bot çalışıyor")

# START
async def main():
    await app.start()
    await call.start()
    print("Bot çalışıyor 🚀")
    await idle()

from pyrogram import idle
asyncio.get_event_loop().run_until_complete(main())
