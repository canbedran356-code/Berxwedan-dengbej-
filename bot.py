"""
🎵 Telegram Asistanlı Müzik Botu
- Telethon session string uyumlu
- py-tgcalls 2.2.x
"""

import asyncio
import os
import logging
from pathlib import Path

import yt_dlp
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream
from pytgcalls.types import StreamEnded          # ✅ Düzeltildi: Update.StreamEnded değil
from pytgcalls.exceptions import NoActiveGroupCall
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID         = int(os.environ.get("API_ID", 0))
API_HASH       = os.environ.get("API_HASH", "")
BOT_TOKEN      = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

bot     = Client("muzik_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
asistan = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
call    = PyTgCalls(asistan)

queue:   dict = {}
current: dict = {}


def format_duration(seconds) -> str:
    if not seconds:
        return "?"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _search_yt(query: str):
    opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        r = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if r and r.get("entries"):
            return r["entries"][0]
    return None


def _get_info(url: str):
    opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def _download_mp3(url: str, out_base: str) -> str:
    opts = {
        "format": "bestaudio/best",
        "outtmpl": out_base,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    mp3 = out_base + ".mp3"
    if Path(mp3).exists():
        return mp3
    for f in Path(out_base).parent.glob(Path(out_base).name + ".*"):
        return str(f)
    return mp3


# ✅ Düzeltildi: on_update handler main() DIŞINDA tanımlandı
@call.on_update()
async def handle_update(update):
    if isinstance(update, StreamEnded):
        chat_id = update.chat_id
        track   = current.pop(chat_id, None)
        if track:
            Path(track["audio_path"]).unlink(missing_ok=True)
        await _play_next(chat_id)


async def _play_next(chat_id: int):
    q = queue.get(chat_id, [])
    if not q:
        try:
            await call.leave_call(chat_id)
        except Exception:
            pass
        return
    next_track       = q.pop(0)
    current[chat_id] = next_track
    try:
        await call.play(chat_id, MediaStream(next_track["audio_path"]))
    except Exception as e:
        logger.error(f"Sonraki şarkı hatası: {e}")
        current.pop(chat_id, None)


@bot.on_message(filters.command("start"))
async def cmd_start(_, msg: Message):
    await msg.reply_text(
        "🎵 **Müzik Botuna Hoş Geldiniz!**\n\n"
        "▶️ `/play <şarkı adı veya YouTube linki>`\n"
        "⏭ `/skip` — Sonraki şarkı\n"
        "⏸ `/pause` — Duraklat\n"
        "▶️ `/resume` — Devam et\n"
        "⏹ `/stop` — Durdur\n"
        "📋 `/queue` — Sıradaki şarkılar\n\n"
        "💡 Önce sesli sohbete katılın, sonra `/play` yazın!"
    )


@bot.on_message(filters.command("play"))
async def cmd_play(_, msg: Message):
    chat_id = msg.chat.id
    if len(msg.command) < 2:
        await msg.reply_text("❌ Kullanım: `/play <şarkı adı veya YouTube linki>`")
        return

    query  = " ".join(msg.command[1:])
    status = await msg.reply_text("🔍 Aranıyor...")
    loop   = asyncio.get_event_loop()

    if query.startswith("http"):
        url = query
        try:
            info = await loop.run_in_executor(None, _get_info, url)
            title    = info.get("title", "Bilinmiyor")
            duration = format_duration(info.get("duration", 0))
        except Exception:
            await status.edit_text("❌ Link geçersiz veya video bulunamadı.")
            return
    else:
        await status.edit_text("🔍 YouTube'da aranıyor...")
        info = await loop.run_in_executor(None, _search_yt, query)
        if not info:
            await status.edit_text("❌ Sonuç bulunamadı.")
            return
        url      = f"https://youtube.com/watch?v={info['id']}"
        title    = info.get("title", "Bilinmiyor")
        duration = format_duration(info.get("duration", 0))

    await status.edit_text(f"⬇️ İndiriliyor: **{title}**...")

    out_base = str(DOWNLOAD_DIR / f"{chat_id}_{abs(hash(url))}")
    try:
        audio_path = await loop.run_in_executor(None, _download_mp3, url, out_base)
    except Exception as e:
        logger.error(f"İndirme hatası: {e}")
        await status.edit_text("❌ İndirme başarısız. Lütfen tekrar deneyin.")
        return

    track = {
        "title": title, "duration": duration,
        "audio_path": audio_path,
        "requested_by": msg.from_user.mention,
    }

    if chat_id in current:
        queue.setdefault(chat_id, []).append(track)
        pos = len(queue[chat_id])
        await status.edit_text(
            f"➕ **Kuyruğa eklendi!**\n\n🎵 {title}\n⏱ {duration}\n📋 Sıra: #{pos}"
        )
    else:
        current[chat_id] = track
        try:
            await call.play(chat_id, MediaStream(audio_path))
            await status.edit_text(
                f"▶️ **Şimdi Çalınıyor!**\n\n🎵 {title}\n⏱ {duration}\n👤 {msg.from_user.mention}"
            )
        except NoActiveGroupCall:
            current.pop(chat_id, None)
            await status.edit_text(
                "❌ Aktif sesli sohbet yok!\n"
                "Grupta bir sesli sohbet başlatın, sonra tekrar deneyin."
            )
        except Exception as e:
            current.pop(chat_id, None)
            logger.error(f"Çalma hatası: {e}")
            await status.edit_text(f"❌ Müzik çalınamadı:\n`{e}`")


@bot.on_message(filters.command("skip"))
async def cmd_skip(_, msg: Message):
    if msg.chat.id not in current:
        await msg.reply_text("❌ Şu an çalan müzik yok.")
        return
    await _play_next(msg.chat.id)
    await msg.reply_text("⏭ Atlandı!")


@bot.on_message(filters.command("pause"))
async def cmd_pause(_, msg: Message):
    try:
        await call.pause_stream(msg.chat.id)
        await msg.reply_text("⏸ Duraklatıldı. `/resume` ile devam et.")
    except Exception:
        await msg.reply_text("❌ Duraklatılamadı.")


@bot.on_message(filters.command("resume"))
async def cmd_resume(_, msg: Message):
    try:
        await call.resume_stream(msg.chat.id)
        await msg.reply_text("▶️ Devam ediliyor!")
    except Exception:
        await msg.reply_text("❌ Devam ettirilemedi.")


@bot.on_message(filters.command("stop"))
async def cmd_stop(_, msg: Message):
    chat_id = msg.chat.id
    try:
        await call.leave_call(chat_id)
        current.pop(chat_id, None)
        queue.pop(chat_id, None)
        await msg.reply_text("⏹ Durduruldu, kanaldan çıkıldı.")
    except Exception:
        await msg.reply_text("❌ Durdurulamadı.")


@bot.on_message(filters.command("queue"))
async def cmd_queue(_, msg: Message):
    chat_id = msg.chat.id
    lines   = []
    if chat_id in current:
        t = current[chat_id]
        lines.append(f"▶️ **Şu an:** {t['title']} [{t['duration']}]")
    q = queue.get(chat_id, [])
    if q:
        lines.append("\n📋 **Sıradakiler:**")
        for i, t in enumerate(q, 1):
            lines.append(f"{i}. {t['title']} [{t['duration']}]")
    await msg.reply_text("\n".join(lines) if lines else "📋 Kuyruk boş.")


async def main():
    missing = [k for k, v in {
        "API_ID": API_ID, "API_HASH": API_HASH,
        "BOT_TOKEN": BOT_TOKEN, "SESSION_STRING": SESSION_STRING,
    }.items() if not v]
    if missing:
        print(f"❌ .env dosyasında eksik: {', '.join(missing)}")
        return

    await asistan.start()
    await bot.start()
    await call.start()

    logger.info("🤖 Bot başlatıldı! Gruba ekleyin ve /play yazın.")
    await idle()
    await call.stop()
    await bot.stop()
    await asistan.disconnect()


if __name__ == "__main__":
    asyncio.run(main())