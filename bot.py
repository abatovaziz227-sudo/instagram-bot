import logging
import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

# linkni tozalash
def clean_url(url):
    return url.split("?")[0]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Instagram video link yubor!")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = clean_url(update.message.text)

    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'best',
            'cookiefile': 'cookies.txt',  # MUHIM
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # video topish
        for file in os.listdir():
            if file.endswith(".mp4"):
                with open(file, "rb") as video:
                    await update.message.reply_video(video)

                os.remove(file)

        await msg.delete()

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
