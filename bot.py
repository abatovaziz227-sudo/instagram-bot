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
            'quiet': True,

            # 🔥 cookies qo‘shildi
            'cookiefile': 'cookies.txt',

            # 🔥 VIDEO + AUDIO birlashtirish
            'format': 'bestvideo+bestaudio/best',

            # 🔥 audio/video merge qilish
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # carousel (bir nechta media) bo‘lsa
            if 'entries' in info:
                info = info['entries'][0]

            filename = ydl.prepare_filename(info)

        # 🔥 VIDEO yoki RASM aniqlash
        if filename.endswith(".mp4"):
            with open(filename, 'rb') as f:
                await update.message.reply_video(f)
        else:
            with open(filename, 'rb') as f:
                await update.message.reply_photo(f)

        await msg.delete()

        if os.path.exists(filename):
            os.remove(filename)

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
