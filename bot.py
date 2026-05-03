import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

QUEUE = {}

# YOUTUBE SEARCH
def yt_search(query):
    ydl_opts = {"format": "bestaudio"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        return info["url"], info["title"]

# PLAY
@app.on_message(filters.command("play"))
async def play(_, msg):
    chat_id = msg.chat.id

    if len(msg.command) < 2:
        return await msg.reply("❌ Şarkı adı yaz")

    query = msg.text.split(None, 1)[1]
    url, title = yt_search(query)

    try:
        await call.join_group_call(
            chat_id,
            AudioPiped(url),
        )
    except:
        await call.change_stream(chat_id, AudioPiped(url))

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("▶️ Resume", callback_data="resume"),
            ],
            [
                InlineKeyboardButton("⏭ Skip", callback_data="skip"),
                InlineKeyboardButton("⏹ Stop", callback_data="stop"),
            ],
        ]
    )

    await msg.reply(f"🎶 Oynatılıyor: {title}", reply_markup=buttons)

# BUTTONS
@app.on_callback_query()
async def cb(_, q):
    chat_id = q.message.chat.id

    if q.data == "pause":
        await call.pause_stream(chat_id)
        await q.answer("Duraklatıldı")

    elif q.data == "resume":
        await call.resume_stream(chat_id)
        await q.answer("Devam ediyor")

    elif q.data == "stop":
        await call.leave_group_call(chat_id)
        await q.answer("Durduruldu")

    elif q.data == "skip":
        await call.leave_group_call(chat_id)
        await q.answer("Geçildi")

# TEST
@app.on_message(filters.command("test"))
async def test(_, msg):
    await msg.reply("Bot çalışıyor ✅")

# START
async def main():
    await app.start()
    await call.start()
    print("Bot çalışıyor 🔥")
    await idle()

asyncio.run(main())
