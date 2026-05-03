# 🎵 Telegram Asistanlı Müzik Botu

Grup sesli sohbetlerine katılarak YouTube'dan müzik çalan bot.  
**Bot** komutları alır, **Asistan** (userbot) ses kanalına girip müzik çalar.

---

## 🏗️ Nasıl Çalışır?

```
Kullanıcı → /play şarkı → Bot → YouTube'dan indir → Asistan → Sesli Sohbet
```

- **Bot:** @BotFather ile oluşturulan normal bot hesabı
- **Asistan:** Sizin kişisel Telegram hesabınız (py-tgcalls ile sesli sohbete girer)

---

## 🚀 Kurulum

### 1. Gereksinimler

```bash
# FFmpeg (zorunlu)
sudo apt install ffmpeg      # Ubuntu/Debian
brew install ffmpeg          # macOS
```

### 2. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 3. API Bilgilerini Al

**a) Telegram API (my.telegram.org):**
1. https://my.telegram.org adresine gidin
2. Telefon numaranızla giriş yapın
3. "API development tools" → "Create application"
4. `API_ID` ve `API_HASH` değerlerini kopyalayın

**b) Bot Token (@BotFather):**
1. Telegram'da @BotFather'a gidin
2. `/newbot` yazın ve talimatları izleyin
3. Token'ı kopyalayın

### 4. Session String Oluştur

```bash
python generate_session.py
```

> Kişisel Telegram hesabınızla (asistan olarak kullanılacak) giriş yapın.  
> Çıkan SESSION_STRING'i kopyalayın.

### 5. .env Dosyası Oluştur

```bash
cp .env.example .env
```

`.env` dosyasını açıp doldurun:

```
API_ID=12345678
API_HASH=abcdef...
BOT_TOKEN=1234567890:ABC...
SESSION_STRING=BQA...
```

### 6. Botu Başlat

```bash
python bot.py
```

---

## 📖 Kullanım

1. **Botu grubunuza ekleyin** ve yönetici yapın
2. **Asistan hesabınızı da gruba ekleyin**
3. Grupta bir **sesli sohbet başlatın**
4. Komutları kullanın:

| Komut | Açıklama |
|-------|----------|
| `/play <şarkı/link>` | Müzik çal veya kuyruğa ekle |
| `/skip` | Sonraki şarkıya geç |
| `/pause` | Duraklat |
| `/resume` | Devam et |
| `/stop` | Durdur ve kanaldan çık |
| `/queue` | Sıradaki şarkıları göster |

---

## ⚠️ Önemli Notlar

- Asistan hesabı gruba **üye** olmalı
- Asistan hesabının **sesli sohbete katılma izni** olmalı
- SESSION_STRING'i **kimseyle paylaşmayın** — bu hesabınıza tam erişim sağlar
- Telegram'ın kullanım şartlarını ihlal etmemek için botu spam amacıyla kullanmayın

---

## 📁 Dosya Yapısı

```
tg-music-bot/
├── bot.py               # Ana bot kodu
├── generate_session.py  # Session string oluşturucu
├── requirements.txt     # Bağımlılıklar
├── .env.example         # Örnek ayar dosyası
├── .env                 # Gerçek ayarlarınız (oluşturmanız gerek)
└── downloads/           # Geçici ses dosyaları (otomatik oluşur)
```
