import logging
import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# logging
logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"
ADMIN_ID = 957915860  # <-- BU YERGA O'Z TELEGRAM IDINGNI QO'Y

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Faqat senga yuboradi
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 Yangi foydalanuvchi:\n👤 {user.full_name}\n🆔 {user.id}"
    )

    await update.message.reply_text("📥 Instagram video link yubor!")

# video yuklash
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    url = update.message.text

    # ADMIN ga xabar
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 Link keldi:\n👤 {user.full_name}\n🔗 {url}"
    )

    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'mp4',
            'quiet': True,
            'cookiefile': 'cookies.txt'   # 🍪 MUHIM
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            await update.message.reply_video(video)

        await msg.delete()

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

# run
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("✅ Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
