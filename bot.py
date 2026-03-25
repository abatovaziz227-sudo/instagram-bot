import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

BOT_TOKEN = os.getenv("8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ishlayapti ✅ Link yubor!")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⏳ Yuklanmoqda...")

    ydl_opts = {
        'format': 'best[filesize<50M]',  # 50MB dan kichik video
        'outtmpl': 'video.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            await update.message.reply_video(video)

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text("❌ Xatolik yoki video juda katta!")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("download", download))

app.run_polling()
