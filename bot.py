import logging
import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Instagram link yubor!")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'outtmpl': 'media.%(ext)s',
            'format': 'best',
            'quiet': True,
            'cookiefile': 'cookies.txt',  # 🔥 MUHIM
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # Agar post ichida bir nechta media bo‘lsa
            if 'entries' in info:
                for entry in info['entries']:
                    filename = ydl.prepare_filename(entry)
                    await send_file(update, filename)
            else:
                filename = ydl.prepare_filename(info)
                await send_file(update, filename)

        await msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def send_file(update, filename):
    try:
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            with open(filename, 'rb') as photo:
                await update.message.reply_photo(photo)
        else:
            with open(filename, 'rb') as video:
                await update.message.reply_video(video)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Yuborishda xato: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("✅ Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
