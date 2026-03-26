import logging
import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Instagram link yubor (video yoki rasm)")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'outtmpl': 'media.%(ext)s',
            'quiet': True,
            'cookiefile': 'cookies.txt',   # 🔥 MUHIM
            'format': 'best',
            'noplaylist': True
        }

        files = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # Agar carousel (bir nechta rasm/video) bo‘lsa
            if 'entries' in info:
                for entry in info['entries']:
                    filename = ydl.prepare_filename(entry)
                    files.append(filename)
            else:
                filename = ydl.prepare_filename(info)
                files.append(filename)

        # 🔥 YUBORISH
        for file in files:
            if file.endswith(".mp4"):
                with open(file, 'rb') as f:
                    await update.message.reply_video(f)
            else:
                with open(file, 'rb') as f:
                    await update.message.reply_photo(f)

        await msg.delete()

        # 🔥 TOZALASH
        for file in files:
            if os.path.exists(file):
                os.remove(file)

    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("✅ Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
