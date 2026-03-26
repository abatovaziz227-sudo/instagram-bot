import logging
import yt_dlp
import instaloader
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

# downloads papka
if not os.path.exists("downloads"):
    os.mkdir("downloads")

# instaloader sozlash
L = instaloader.Instaloader(
    dirname_pattern="downloads",
    save_metadata=False,
    download_video_thumbnails=False
)

# linkdan shortcode olish
def get_shortcode(url):
    match = re.search(r"/(p|reel)/([^/?]+)", url)
    return match.group(2) if match else None


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
        # eski fayllarni tozalash
        for f in os.listdir("downloads"):
            os.remove(os.path.join("downloads", f))

        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # 🔥 VIDEO bo‘lsa (yt-dlp bilan)
        if post.is_video:
            ydl_opts = {
                'outtmpl': 'video.%(ext)s',
                'format': 'best',
                'cookiefile': 'cookies.txt',
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)

            for file in os.listdir():
                if file.endswith(".mp4"):
                    with open(file, "rb") as f:
                        await update.message.reply_video(f)
                    os.remove(file)

        # 🔥 RASM yoki CAROUSEL (instaloader bilan)
        else:
            L.download_post(post, target="downloads")

            files = os.listdir("downloads")

            videos = [f for f in files if f.endswith(".mp4")]
            images = [f for f in files if f.endswith(".jpg")]

            # video bo‘lsa (carousel ichida)
            for file in videos:
                with open(os.path.join("downloads", file), "rb") as f:
                    await update.message.reply_video(f)

            # rasmlar
            for file in images:
                with open(os.path.join("downloads", file), "rb") as f:
                    await update.message.reply_photo(f)

        # tozalash
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
