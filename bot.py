import logging
import os
import re
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

# papka yaratish
if not os.path.exists("downloads"):
    os.mkdir("downloads")

L = instaloader.Instaloader(dirname_pattern="downloads")

# 🔥 LINKDAN SHORTCODE AJRATADI
def get_shortcode(url):
    match = re.search(r"/p/([^/?]+)", url)
    if match:
        return match.group(1)

    match = re.search(r"/reel/([^/?]+)", url)
    if match:
        return match.group(1)

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

        # 🔥 yuklab olish
        L.download_post(post, target="downloads")

        # 🔥 yuborish
        for file in os.listdir("downloads"):
            path = os.path.join("downloads", file)

            if file.endswith(".mp4"):
                with open(path, "rb") as f:
                    await update.message.reply_video(f)

            elif file.endswith(".jpg"):
                with open(path, "rb") as f:
                    await update.message.reply_photo(f)

            os.remove(path)

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
