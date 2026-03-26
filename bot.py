import logging
import yt_dlp
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"
ADMIN_ID = 957915860

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 Yangi user:\n👤 {user.full_name}\n🆔 {user.id}"
    )

    await update.message.reply_text("📥 Instagram link yubor!")

# download (VIDEO + RASM)
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    url = update.message.text

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 Link:\n👤 {user.full_name}\n🔗 {url}"
    )

    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # 🔥 Agar bir nechta media bo‘lsa (carousel)
        if 'entries' in info:
            for entry in info['entries']:
                filename = ydl.prepare_filename(entry)

                if filename.endswith(('.mp4', '.mkv', '.webm')):
                    with open(filename, 'rb') as f:
                        await update.message.reply_video(f)
                else:
                    with open(filename, 'rb') as f:
                        await update.message.reply_photo(f)

                if os.path.exists(filename):
                    os.remove(filename)

        else:
            filename = ydl.prepare_filename(info)

            # 🔥 Video yoki rasmni aniqlash
            if filename.endswith(('.mp4', '.mkv', '.webm')):
                with open(filename, 'rb') as f:
                    await update.message.reply_video(f)
            else:
                with open(filename, 'rb') as f:
                    await update.message.reply_photo(f)

            if os.path.exists(filename):
                os.remove(filename)

        await msg.delete()

    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

# main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("✅ Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
