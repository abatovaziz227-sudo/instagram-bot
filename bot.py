import logging
import os
import re
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

# papka
if not os.path.exists("downloads"):
    os.mkdir("downloads")

L = instaloader.Instaloader(dirname_pattern="downloads", save_metadata=False)

def get_shortcode(url):
    match = re.search(r"/(p|reel)/([^/?]+)", url)
    if match:
        return match.group(2)
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Instagram link yubor!")


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    shortcode = get_shortcode(url)

    if not shortcode:
        await update.message.reply_text("❌ Noto‘g‘ri link!")
        return

    await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # 🔥 tozalash (eski fayllarni o‘chir)
        for f in os.listdir("downloads"):
            os.remove(os.path.join("downloads", f))

        # 🔥 yuklab olish
        L.download_post(post, target="downloads")

        files = os.listdir("downloads")

        # 🔥 faqat kerakli fayllarni ajratamiz
        images = [f for f in files if f.endswith(".jpg")]
        videos = [f for f in files if f.endswith(".mp4")]

        # 🔥 AVVAL VIDEO YUBORAMIZ
        for file in videos:
            with open(os.path.join("downloads", file), "rb") as f:
                await update.message.reply_video(f)

        # 🔥 KEYIN RASMLAR
        for file in images:
            with open(os.path.join("downloads", file), "rb") as f:
                await update.message.reply_photo(f)

        # 🔥 tozalash
        for f in os.listdir("downloads"):
            os.remove(os.path.join("downloads", f))

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
