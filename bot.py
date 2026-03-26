import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8793753588:AAHl8bYf6jLt8GiTlP3gBL_xTmIDRuUHU4c"

# 🔥 API URL
API = "https://api.akuari.my.id/downloader/ig?url="


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Instagram link yubor!")


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        res = requests.get(API + url).json()

        if not res["status"]:
            await update.message.reply_text("❌ Topilmadi!")
            return

        data = res["result"]

        # 🔥 VIDEO
        if "video" in data:
            await update.message.reply_video(data["video"])

        # 🔥 RASM
        if "image" in data:
            for img in data["image"]:
                await update.message.reply_photo(img)

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
