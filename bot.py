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
            'cookiefile': 'cookies.txt',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # 🔥 AGAR POSTDA KO‘P MEDIA BO‘LSA (carousel)
        if 'entries' in info:
            for entry in info['entries']:
                await send_media(entry, update)
        else:
            await send_media(info, update)

        await msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")


# 🔥 MEDIA YUBORISH FUNKSIYASI
async def send_media(info, update):
    try:
        ydl_opts = {
            'outtmpl': 'media.%(ext)s',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(info['webpage_url'], download=True)
            filename = ydl.prepare_filename(result)

        # 🔥 AGAR VIDEO BO‘LSA
        if filename.endswith(".mp4"):
            with open(filename, 'rb') as f:
                await update.message.reply_video(f)

        # 🔥 AGAR RASM BO‘LSA
        elif filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            with open(filename, 'rb') as f:
                await update.message.reply_photo(f)

        # 🔥 ba’zi hollarda rasm URL orqali keladi
        elif 'thumbnail' in result:
            await update.message.reply_photo(result['thumbnail'])

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Media xato: {e}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("✅ Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
