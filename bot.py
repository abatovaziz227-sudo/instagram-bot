import logging
import yt_dlp
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# logging
logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"
ADMIN_ID = 957915860  # o'zingning telegram id

# userlar
users = set()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users.add(user.id)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 Yangi user:\n👤 {user.full_name}\n🆔 {user.id}\n👥 Jami: {len(users)}"
    )

    await update.message.reply_text("📥 Instagram link yubor!")

# download (video + rasm)
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users.add(user.id)

    url = update.message.text

    print(f"USER: {user.id} | LINK: {url}")

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 Link:\n👤 {user.full_name}\n🔗 {url}"
    )

    msg = await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            'format': 'best',
            'writethumbnail': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # 🔥 barcha fayllarni tekshiramiz
        for file in os.listdir():
            if file.endswith(('.mp4', '.mkv', '.webm')):
                with open(file, 'rb') as f:
                    await update.message.reply_video(f)

            elif file.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                with open(file, 'rb') as f:
                    await update.message.reply_photo(f)

            # faylni o‘chiramiz
            try:
                os.remove(file)
            except:
                pass

        await msg.delete()

    except Exception as e:
        print("XATO:", e)
        await update.message.reply_text(f"❌ Xato: {e}")

# stats (faqat admin)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"👥 Jami foydalanuvchi: {len(users)}")

# main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("✅ Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
