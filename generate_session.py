import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID   = 35642398
API_HASH = "193db28dd86165f10415f31303edd22b"
TELEFON  = "+41782264496"

async def generate():
    print("Baglaniyor...")
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        await client.start(phone=TELEFON)
        session = client.session.save()
        print("\n" + "="*50)
        print("SESSION_STRING:")
        print(session)
        print("="*50)
        print(".env dosyasina SESSION_STRING= satirina yapistirin.")

asyncio.run(generate())
