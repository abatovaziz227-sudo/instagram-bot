import logging
import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# logging
logging.basicConfig(level=logging.INFO)

# TOKEN (BU YERGA O'Z TOKENINGNI QO'Y)
TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Instagram video link yubor!")

# video yuklash funksiyasi
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'mp4',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # video yuborish
        with open(filename, 'rb') as video:
            await update.message.reply_video(video)

        await msg.delete()

        # faylni o‘chirish (joy tozalanadi)
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        if "Timed out" in str(e):
            pass
        else:
            await update.message.reply_text(f"❌ Xato: {e}")

# botni ishga tushirish
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("✅ Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
users = set()

async def start(update, context):
    users.add(update.message.from_user.id)
    await update.message.reply_text("Salom!")
    print("Userlar soni:", len(users))
